[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$DestinationRoot = ".worktrees"
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $output = & git -C $WorkingDirectory @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed in '$WorkingDirectory' with exit code $exitCode`n$($output -join "`n")"
    }

    if ($null -eq $output) {
        return @()
    }

    return @($output)
}

function Get-FirstLine {
    param([Parameter(Mandatory = $true)][object[]]$Lines)

    if ($Lines.Count -eq 0 -or $null -eq $Lines[0]) {
        return ""
    }

    return [string]$Lines[0]
}

function Normalize-Path {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
}

function Test-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $normalizedPath = Normalize-Path $Path
    $normalizedRoot = Normalize-Path $Root
    $prefix = $normalizedRoot + [System.IO.Path]::DirectorySeparatorChar

    return (
        $normalizedPath.Equals($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        $normalizedPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
    )
}

function Get-Worktrees {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $lines = Invoke-Git -WorkingDirectory $RepoRoot -Arguments @('worktree', 'list', '--porcelain')
    $records = @()
    $current = $null

    foreach ($line in $lines) {
        if ($line -like 'worktree *') {
            if ($null -ne $current) {
                $records += [pscustomobject]$current
            }

            $current = @{
                Path = $line.Substring(9)
                Head = $null
                Branch = $null
                Detached = $false
                Bare = $false
                Prunable = $false
                Locked = $false
                LockReason = $null
            }
            continue
        }

        if ($null -eq $current) {
            continue
        }

        if ($line -like 'HEAD *') {
            $current.Head = $line.Substring(5)
        }
        elseif ($line -like 'branch *') {
            $current.Branch = $line.Substring(7) -replace '^refs/heads/', ''
        }
        elseif ($line -eq 'detached') {
            $current.Detached = $true
        }
        elseif ($line -eq 'bare') {
            $current.Bare = $true
        }
        elseif ($line -like 'prunable*') {
            $current.Prunable = $true
        }
        elseif ($line -eq 'locked') {
            $current.Locked = $true
        }
        elseif ($line -like 'locked *') {
            $current.Locked = $true
            $current.LockReason = $line.Substring(7)
        }
    }

    if ($null -ne $current) {
        $records += [pscustomobject]$current
    }

    return @($records)
}

function Resolve-WorktreeRecord {
    param(
        [Parameter(Mandatory = $true)]$Record,
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    $registeredPath = Normalize-Path $Record.Path
    $source = $registeredPath
    $needsRepair = $false

    # Historical Orca/worktree maintenance left a few Git administrative
    # registrations pointing at <worktree>/.git rather than the worktree root.
    # Git's documented repair command can reconnect these records, but dry-run
    # must remain mutation-free. Resolve the actual parent worktree here and
    # only perform `git worktree repair` in -Apply mode after full preflight.
    if ((Split-Path -Leaf $registeredPath) -eq '.git') {
        $candidate = Normalize-Path (Split-Path -Parent $registeredPath)

        if (-not (Test-Path -LiteralPath $candidate)) {
            throw "Malformed registered path '$registeredPath' has no existing parent worktree '$candidate'."
        }

        $topLevel = (Get-FirstLine -Lines (Invoke-Git -WorkingDirectory $candidate -Arguments @('rev-parse', '--show-toplevel'))).Trim()
        if (-not $topLevel) {
            throw "Could not resolve a worktree root for malformed registration '$registeredPath'."
        }

        $topLevel = Normalize-Path $topLevel
        if (-not $topLevel.Equals($candidate, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Malformed registration '$registeredPath' resolves through parent '$candidate' to unexpected top-level '$topLevel'."
        }

        $source = $candidate
        $needsRepair = $true
    }

    $actualHead = (Get-FirstLine -Lines (Invoke-Git -WorkingDirectory $source -Arguments @('rev-parse', 'HEAD'))).Trim()
    $actualBranch = (Get-FirstLine -Lines (Invoke-Git -WorkingDirectory $source -Arguments @('branch', '--show-current'))).Trim()

    if ($actualHead -ne $Record.Head) {
        throw "HEAD mismatch for '$source': worktree list=$($Record.Head), actual=$actualHead"
    }

    if (-not $Record.Detached -and $actualBranch -ne $Record.Branch) {
        throw "Branch mismatch for '$source': worktree list=$($Record.Branch), actual=$actualBranch"
    }

    return [pscustomobject]@{
        RegisteredPath = $registeredPath
        Source = $source
        NeedsRepair = $needsRepair
        Head = $actualHead
        Branch = $(if ($Record.Detached) { '(detached)' } else { $actualBranch })
        Detached = $Record.Detached
        Bare = $Record.Bare
        Prunable = $Record.Prunable
        Locked = $Record.Locked
        LockReason = $Record.LockReason
    }
}

function Get-Category {
    param([Parameter(Mandatory = $true)][string]$LeafName)

    if ($LeafName -like 'TASK-*') {
        return 'tasks'
    }

    if (
        $LeafName -like 'governance-*' -or
        $LeafName -like 'GOV-*' -or
        $LeafName -like 'PRE-*' -or
        $LeafName -like 'continuous-integration-*'
    ) {
        return 'maintenance'
    }

    return 'other'
}

$rootLines = Invoke-Git -WorkingDirectory (Get-Location).Path -Arguments @('rev-parse', '--show-toplevel')
$repoRoot = (Get-FirstLine -Lines $rootLines).Trim()
if (-not $repoRoot) {
    throw 'Could not resolve the repository root.'
}

$repoRoot = Normalize-Path $repoRoot
$destinationRootFull = Normalize-Path (Join-Path $repoRoot $DestinationRoot)

Write-Host "Repository root: $repoRoot"
Write-Host "Destination root: $destinationRootFull"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY RUN' })"
Write-Host ""

$worktreesBefore = Get-Worktrees -RepoRoot $repoRoot
if ($worktreesBefore.Count -lt 1) {
    throw 'No Git worktrees were detected.'
}

$resolvedRecords = @()
foreach ($record in $worktreesBefore) {
    $resolvedRecords += Resolve-WorktreeRecord -Record $record -RepoRoot $repoRoot
}

$rootRecord = $resolvedRecords | Where-Object {
    $_.Source.Equals($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)
}
if ($null -eq $rootRecord) {
    throw "The current repository root '$repoRoot' was not present in 'git worktree list --porcelain'."
}

$plans = @()
$skipped = @()
$repairPlans = @()

foreach ($record in $resolvedRecords) {
    $source = $record.Source

    if ($source.Equals($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        $skipped += [pscustomobject]@{
            Path = $source
            Reason = 'root worktree'
        }
        continue
    }

    if (-not (Test-PathUnderRoot -Path $source -Root $repoRoot)) {
        $skipped += [pscustomobject]@{
            Path = $source
            Reason = 'registered worktree is outside repository root'
        }
        continue
    }

    if ($record.Locked) {
        $reason = $(if ($record.LockReason) { $record.LockReason } else { 'no reason recorded' })
        throw "Registered worktree is locked and will not be moved automatically: '$source' ($reason)."
    }

    $destinationPrefix = $destinationRootFull + [System.IO.Path]::DirectorySeparatorChar
    if (
        $source.Equals($destinationRootFull, [System.StringComparison]::OrdinalIgnoreCase) -or
        $source.StartsWith($destinationPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    ) {
        $skipped += [pscustomobject]@{
            Path = $source
            Reason = 'already consolidated under destination root'
        }
        continue
    }

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Registered worktree path does not exist: $source"
    }

    $leaf = Split-Path -Leaf $source
    $category = Get-Category -LeafName $leaf
    $destination = Normalize-Path (Join-Path (Join-Path $destinationRootFull $category) $leaf)

    if (Test-Path -LiteralPath $destination) {
        throw "Destination collision: '$destination' already exists. Nothing has been moved."
    }

    $statusLines = @(Invoke-Git -WorkingDirectory $source -Arguments @('status', '--porcelain=v1'))
    $submoduleLines = @(Invoke-Git -WorkingDirectory $source -Arguments @('submodule', 'status', '--recursive'))
    if ($submoduleLines.Count -gt 0) {
        throw "Worktree '$source' contains configured submodule entries and will not be moved automatically."
    }

    if ($record.NeedsRepair) {
        $repairPlans += [pscustomobject]@{
            RegisteredPath = $record.RegisteredPath
            WorktreeRoot = $source
            Branch = $record.Branch
            Head = $record.Head
        }
    }

    $plans += [pscustomobject]@{
        Source = $source
        RegisteredPath = $record.RegisteredPath
        Destination = $destination
        Category = $category
        Branch = $record.Branch
        Head = $record.Head
        DirtyEntries = $statusLines.Count
        StatusBefore = @($statusLines)
        NeedsAdministrativeRepair = $record.NeedsRepair
    }
}

if ($repairPlans.Count -gt 0) {
    Write-Host 'Administrative registration repairs required before move:'
    $repairPlans |
        Select-Object Branch, Head, RegisteredPath, WorktreeRoot |
        Format-Table -AutoSize
    Write-Host ""
    Write-Host "Required repairs: $($repairPlans.Count)"
    Write-Host 'DRY RUN does not mutate these registrations; APPLY repairs each malformed registration from inside its verified linked-worktree root after all preflight checks pass.'
    Write-Host ""
}

if ($plans.Count -eq 0) {
    Write-Host 'No registered child worktrees need consolidation.'
    if ($skipped.Count -gt 0) {
        Write-Host ''
        Write-Host 'Skipped:'
        $skipped | Format-Table -AutoSize
    }
    exit 0
}

Write-Host 'Planned registered worktree moves:'
$plans |
    Select-Object Category, Branch, Head, DirtyEntries, NeedsAdministrativeRepair, Source, Destination |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Planned moves: $($plans.Count)"
Write-Host "Administrative repairs required: $($repairPlans.Count)"
Write-Host 'No unregistered directory will be touched.'

if (-not $Apply) {
    Write-Host ""
    Write-Host 'DRY RUN ONLY. Re-run with -Apply after reviewing the plan.'
    exit 0
}

if ($repairPlans.Count -gt 0) {
    Write-Host ""
    Write-Host 'Repairing malformed Git worktree administrative registrations from the linked worktree roots...'

    foreach ($repair in $repairPlans) {
        Write-Host "REPAIR: $($repair.RegisteredPath) -> $($repair.WorktreeRoot)"

        # Git documents that a linked worktree whose connection is stale can
        # repair that connection by running `git worktree repair` from inside
        # the linked worktree itself. This avoids asking the main worktree to
        # traverse the malformed registered path before it has been repaired.
        Invoke-Git -WorkingDirectory $repair.WorktreeRoot -Arguments @('worktree', 'repair') | Out-Null

        $afterSingleRepair = Get-Worktrees -RepoRoot $repoRoot
        if ($afterSingleRepair.Count -ne $worktreesBefore.Count) {
            throw "Worktree count changed during administrative repair of '$($repair.WorktreeRoot)': before=$($worktreesBefore.Count), after=$($afterSingleRepair.Count)"
        }

        $match = $afterSingleRepair | Where-Object {
            (Normalize-Path $_.Path).Equals($repair.WorktreeRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }

        if ($null -eq $match) {
            throw "Administrative repair from linked root did not register expected worktree root '$($repair.WorktreeRoot)'."
        }

        if ($match.Head -ne $repair.Head) {
            throw "Administrative repair changed HEAD for '$($repair.WorktreeRoot)': expected $($repair.Head), got $($match.Head)"
        }

        if ($repair.Branch -ne '(detached)' -and $match.Branch -ne $repair.Branch) {
            throw "Administrative repair changed branch for '$($repair.WorktreeRoot)': expected $($repair.Branch), got $($match.Branch)"
        }
    }

    $afterRepair = Get-Worktrees -RepoRoot $repoRoot
    if ($afterRepair.Count -ne $worktreesBefore.Count) {
        throw "Worktree count changed during administrative repair: before=$($worktreesBefore.Count), after=$($afterRepair.Count)"
    }

    foreach ($repair in $repairPlans) {
        $match = $afterRepair | Where-Object {
            (Normalize-Path $_.Path).Equals($repair.WorktreeRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }

        if ($null -eq $match) {
            throw "Administrative repair did not register expected worktree root '$($repair.WorktreeRoot)'."
        }

        if ($match.Head -ne $repair.Head) {
            throw "Administrative repair changed HEAD for '$($repair.WorktreeRoot)': expected $($repair.Head), got $($match.Head)"
        }

        if ($repair.Branch -ne '(detached)' -and $match.Branch -ne $repair.Branch) {
            throw "Administrative repair changed branch for '$($repair.WorktreeRoot)': expected $($repair.Branch), got $($match.Branch)"
        }
    }

    Write-Host "Administrative repair PASS: $($repairPlans.Count) registration(s)."
}

Write-Host ""
Write-Host 'Applying moves with git worktree move...'

foreach ($plan in $plans) {
    $parent = Split-Path -Parent $plan.Destination
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    Write-Host "MOVE: $($plan.Source) -> $($plan.Destination)"
    Invoke-Git -WorkingDirectory $repoRoot -Arguments @('worktree', 'move', $plan.Source, $plan.Destination) | Out-Null

    $newHead = (Get-FirstLine -Lines (Invoke-Git -WorkingDirectory $plan.Destination -Arguments @('rev-parse', 'HEAD'))).Trim()
    $newBranch = (Get-FirstLine -Lines (Invoke-Git -WorkingDirectory $plan.Destination -Arguments @('branch', '--show-current'))).Trim()
    $statusAfter = @(Invoke-Git -WorkingDirectory $plan.Destination -Arguments @('status', '--porcelain=v1'))

    if ($newHead -ne $plan.Head) {
        throw "Post-move HEAD verification failed for '$($plan.Destination)': expected $($plan.Head), got $newHead"
    }

    if ($plan.Branch -ne '(detached)' -and $newBranch -ne $plan.Branch) {
        throw "Post-move branch verification failed for '$($plan.Destination)': expected $($plan.Branch), got $newBranch"
    }

    if (($statusAfter -join "`n") -ne ($plan.StatusBefore -join "`n")) {
        throw "Post-move working-tree status changed for '$($plan.Destination)'. No destructive recovery was attempted."
    }
}

$worktreesAfter = Get-Worktrees -RepoRoot $repoRoot
if ($worktreesAfter.Count -ne $worktreesBefore.Count) {
    throw "Registered worktree count changed after consolidation: before=$($worktreesBefore.Count), after=$($worktreesAfter.Count)"
}

foreach ($plan in $plans) {
    $match = $worktreesAfter | Where-Object {
        (Normalize-Path $_.Path).Equals((Normalize-Path $plan.Destination), [System.StringComparison]::OrdinalIgnoreCase)
    }

    if ($null -eq $match) {
        throw "Moved worktree is missing from Git registration: $($plan.Destination)"
    }

    if ($match.Head -ne $plan.Head) {
        throw "Final registered HEAD mismatch for '$($plan.Destination)': expected $($plan.Head), got $($match.Head)"
    }

    if ($plan.Branch -ne '(detached)' -and $match.Branch -ne $plan.Branch) {
        throw "Final registered branch mismatch for '$($plan.Destination)': expected $($plan.Branch), got $($match.Branch)"
    }
}

Write-Host ""
Write-Host "CONSOLIDATION PASS: moved $($plans.Count) registered child worktree(s)."
Write-Host "Administrative registrations repaired: $($repairPlans.Count)"
Write-Host "Root worktree preserved: $repoRoot"
Write-Host 'No content deletion, reset, clean, stash, checkout, branch deletion, or unregistered-directory move was performed.'
