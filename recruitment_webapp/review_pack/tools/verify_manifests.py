from pathlib import Path
import hashlib, re, sys

ROOT = Path(__file__).resolve().parents[2]
TARGETS = [ROOT/'review_pack', ROOT/'design_system', ROOT/'responsive_prototype']

row_re = re.compile(r'^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$', re.M)
failures=[]
checks=0

for folder in TARGETS:
    manifest=folder/'MANIFEST.md'
    label=(manifest.read_text(encoding='utf-8').splitlines()[0].replace('# MANIFEST — ','').strip() if manifest.exists() else folder.name)
    if not manifest.exists():
        failures.append(f'{label}: MANIFEST.md missing')
        continue
    text=manifest.read_text(encoding='utf-8')
    rows=row_re.findall(text)
    expected={name:(int(size),digest) for name,size,digest in rows}
    actual=[]
    for p in folder.rglob('*'):
        if not p.is_file():
            continue
        rel=p.relative_to(folder).as_posix()
        if rel == 'MANIFEST.md' or '__pycache__' in rel or rel.endswith('.pyc'):
            continue
        actual.append(rel)
    actual=set(actual)
    expected_names=set(expected)
    missing=sorted(expected_names-actual)
    unlisted=sorted(actual-expected_names)
    checks += 2
    if missing: failures.append(f'{label}: listed-but-missing: {missing}')
    if unlisted: failures.append(f'{label}: unlisted files: {unlisted}')
    for rel in sorted(actual & expected_names):
        p=folder/rel
        data=p.read_bytes()
        size=len(data)
        digest=hashlib.sha256(data).hexdigest()
        exp_size, exp_digest=expected[rel]
        checks += 2
        if size != exp_size:
            failures.append(f'{label}: size mismatch {rel}: {size} != {exp_size}')
        if digest != exp_digest:
            failures.append(f'{label}: sha256 mismatch {rel}: {digest} != {exp_digest}')
    m=re.search(r'(?:Entries|Files \(excluding MANIFEST\.md\)):\s*\*\*(\d+)\*\*', text)
    checks += 1
    if not m or int(m.group(1)) != len(expected):
        failures.append(f'{label}: declared manifest entry count mismatch')

if failures:
    print(f'MANIFEST VERIFICATION FAIL — checks={checks} failures={len(failures)}')
    for f in failures: print('FAIL |', f)
    sys.exit(1)
print(f'MANIFEST VERIFICATION PASS — checks={checks} failures=0')
for folder in TARGETS:
    manifest=folder/'MANIFEST.md'; label=manifest.read_text(encoding='utf-8').splitlines()[0].replace('# MANIFEST — ','').strip(); print('PASS |', label, '|', manifest)
