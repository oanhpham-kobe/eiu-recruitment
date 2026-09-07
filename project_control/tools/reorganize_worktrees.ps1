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

    return @($output)
}

function Normalize-Path {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
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
    }

    if ($null -ne $current) {
        $records += [pscustomobject]$current
    }

    return @($records)
}

function Get-Category {
    param([Parameter(Mandatory = $true)][string]$LeafName)

    if ($LeafName -like 'TASK-*') {
        return 'tasks'
    }

    if (
        $LeafName -like 'governance-*' -or
        $LeafName -like 'GOV-*' -or
        $LeafName -like 'PRE-*'
    ) {
        return 'maintenance'
    }

    return 'other'
}

$repoRoot = (Invoke-Git -WorkingDirectory (Get-Location).Path -Arguments @('rev-parse', '--show-toplevel'))[0].Trim()
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

$rootRecord = $worktreesBefore | Where-Object { (Normalize-Path $_.Path) -eq $repoRoot }
if ($null -eq $rootRecord) {
    throw "The current repository root '$repoRoot' was not present in 'git worktree list --porcelain'."
}

$plans = @()
$skipped = @()

foreach ($record in $worktreesBefore) {
    $source = Normalize-Path $record.Path

    if ($source -eq $repoRoot) {
        $skipped += [pscustomobject]@{
            Path = $source
            Reason = 'root worktree'
        }
        continue
    }

    $repoPrefix = $repoRoot + [System.IO.Path]::DirectorySeparatorChar
    if (-not $source.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        $skipped += [pscustomobject]@{
            Path = $source
            Reason = 'registered worktree is outside repository root'
        }
        continue
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

    $actualHead = (Invoke-Git -WorkingDirectory $source -Arguments @('rev-parse', 'HEAD'))[0].Trim()
    $actualBranch = (Invoke-Git -WorkingDirectory $source -Arguments @('branch', '--show-current'))[0].Trim()
    $statusLines = Invoke-Git -WorkingDirectory $source -Arguments @('status', '--porcelain=v1')

    if ($actualHead -ne $record.Head) {
        throw "HEAD mismatch before move for '$source': worktree list=$($record.Head), actual=$actualHead"
    }

    if (-not $record.Detached -and $actualBranch -ne $record.Branch) {
        throw "Branch mismatch before move for '$source': worktree list=$($record.Branch), actual=$actualBranch"
    }

    $plans += [pscustomobject]@{
        Source = $source
        Destination = $destination
        Category = $category
        Branch = $(if ($record.Detached) { '(detached)' } else { $actualBranch })
        Head = $actualHead
        DirtyEntries = @($statusLines).Count
    }
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
    Select-Object Category, Branch, Head, DirtyEntries, Source, Destination |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Planned moves: $($plans.Count)"
Write-Host 'No unregistered directory will be touched.'

if (-not $Apply) {
    Write-Host ""
    Write-Host 'DRY RUN ONLY. Re-run with -Apply after reviewing the plan.'
    exit 0
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

    $newHead = (Invoke-Git -WorkingDirectory $plan.Destination -Arguments @('rev-parse', 'HEAD'))[0].Trim()
    $newBranch = (Invoke-Git -WorkingDirectory $plan.Destination -Arguments @('branch', '--show-current'))[0].Trim()

    if ($newHead -ne $plan.Head) {
        throw "Post-move HEAD verification failed for '$($plan.Destination)': expected $($plan.Head), got $newHead"
    }

    if ($plan.Branch -ne '(detached)' -and $newBranch -ne $plan.Branch) {
        throw "Post-move branch verification failed for '$($plan.Destination)': expected $($plan.Branch), got $newBranch"
    }
}

$worktreesAfter = Get-Worktrees -RepoRoot $repoRoot

foreach ($plan in $plans) {
    $match = $worktreesAfter | Where-Object {
        (Normalize-Path $_.Path) -eq (Normalize-Path $plan.Destination)
    }

    if ($null -eq $match) {
        throw "Moved worktree is missing from Git registration: $($plan.Destination)"
    }
}

Write-Host ""
Write-Host "CONSOLIDATION PASS: moved $($plans.Count) registered child worktree(s)."
Write-Host "Root worktree preserved: $repoRoot"
Write-Host 'No content deletion, reset, clean, stash, checkout, branch deletion, or unregistered-directory move was performed.'
