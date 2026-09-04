from pathlib import Path
import sys,argparse,yaml
B=Path(__file__).resolve().parents[1]
def sources():
    reg=yaml.safe_load((B/'source_registry.yaml').read_text(encoding='utf-8'))
    return [B/x['file'] for x in reg['documents'] if x.get('status')=='CURRENT' and x.get('normative') and (B/x['file']).exists()]
def render():
    parts=['# 15. ALL-IN-ONE SPEC — GENERATED v1.17','', '> DO NOT EDIT MANUALLY. Generated deterministically from CURRENT normative numbered modules listed in `source_registry.yaml`.', '> HISTORICAL/SUPERSEDED review and gate documents are excluded from the normative body.', '> Regenerate after source changes; validation fails on byte drift.','']
    for p in sources(): parts += ['\n---\n',f'<!-- SOURCE: {p.name} -->\n',p.read_text(encoding='utf-8').rstrip(),'\n']
    return '\n'.join(parts).rstrip()+'\n'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--stdout',action='store_true'); a=ap.parse_args(); data=render(); target=B/'15_ALL_IN_ONE_SPEC.md'
    if a.stdout: sys.stdout.write(data); return
    if a.check:
        if not target.exists() or target.read_text(encoding='utf-8')!=data: print('FAIL: All-in-One differs from CURRENT-only regeneration'); sys.exit(1)
        print('PASS: All-in-One CURRENT-only deterministic equality'); return
    target.write_text(data,encoding='utf-8'); print(f'Generated {target.name} from {len(sources())} CURRENT sources')
if __name__=='__main__': main()
