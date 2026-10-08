from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from typing import Any
from src.bod_evidence_envelope import EvidenceEnvelopeError, EvidenceEnvelopeV0_1, EvidenceReferenceV0_1, create_evidence_envelope, verify_chain

def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def canonical_json(value: Any) -> bytes: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def repository_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve(); raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]); files = [Path(p.decode()) for p in raw.split(b"\0") if p]
    entries = [{"path": rel.as_posix(), "sha256": sha256_bytes((root / rel).read_bytes()), "size": (root / rel).stat().st_size} for rel in sorted(files, key=lambda p: p.as_posix())]
    durable = {"schema":"bod-repository-snapshot-v0.1","files":entries}; return {**durable,"state_root":sha256_bytes(b"BOD-REPOSITORY-SNAPSHOT-V0.1\0"+canonical_json(durable))}
def load(path): return json.loads(Path(path).read_text())
def save(path,value): Path(path).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def cmd_snapshot(a):
    value=repository_snapshot(Path(a.path));
    if a.out: save(a.out,value)
    print(json.dumps(value,indent=2)); return 0
def cmd_create(a):
    refs=[EvidenceReferenceV0_1.from_document(x) for x in load(a.evidence)] if a.evidence else []
    env=create_evidence_envelope(project_id=a.project,protocol_version="0.1",state_root=a.state_root,predecessor_state_root=a.predecessor,transition_id=a.transition,evidence=refs,capture_boundary=a.capture_boundary); value=env.to_document()
    if a.out: save(a.out,value)
    print(json.dumps(value,indent=2)); return 0
def parse_envelopes(value):
    if isinstance(value,dict) and "envelopes" in value: value=value["envelopes"]
    if isinstance(value,dict): value=[value]
    if not isinstance(value,list): raise EvidenceEnvelopeError("expected envelope object or envelopes array")
    return [EvidenceEnvelopeV0_1.from_document(x) for x in value]
def cmd_verify(a):
    try:
        envs=parse_envelopes(load(a.file));
        if a.chain: verify_chain(envs)
        elif len(envs)!=1: raise EvidenceEnvelopeError("verify without --chain requires exactly one envelope")
        print(json.dumps({"status":"VALID","envelopes":len(envs),"commitments":[e.commitment() for e in envs]},indent=2)); return 0
    except (EvidenceEnvelopeError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"INVALID","reason":str(exc)},indent=2)); return 1
def cmd_demo(a):
    previous=None; chain=[]
    for i in range(3):
        state=sha256_bytes(f"BOD-demo-state-{i}".encode()); env=create_evidence_envelope(project_id="bod-demo",protocol_version="0.1",state_root=state,predecessor_state_root=previous,transition_id=f"demo-transition-{i}",evidence=[EvidenceReferenceV0_1("demo",sha256_bytes(f"evidence-{i}".encode()),"text/plain")],capture_boundary="demo"); chain.append(env); previous=state
    verify_chain(chain); print(json.dumps({"status":"VALID","product":"BOD Evidence Fabric","states":len(chain),"head":chain[-1].state_root,"envelope_ids":[e.envelope_id for e in chain]},indent=2)); return 0
def main():
    p=argparse.ArgumentParser(prog="bod",description="BOD Evidence Fabric"); s=p.add_subparsers(dest="command",required=True)
    x=s.add_parser("snapshot"); x.add_argument("path",nargs="?",default="."); x.add_argument("--out"); x.set_defaults(func=cmd_snapshot)
    x=s.add_parser("evidence-create"); x.add_argument("--project",required=True); x.add_argument("--state-root",required=True); x.add_argument("--transition",required=True); x.add_argument("--predecessor"); x.add_argument("--capture-boundary",default="repository-state"); x.add_argument("--evidence"); x.add_argument("--out"); x.set_defaults(func=cmd_create)
    x=s.add_parser("verify"); x.add_argument("file"); x.add_argument("--chain",action="store_true"); x.set_defaults(func=cmd_verify)
    x=s.add_parser("demo"); x.set_defaults(func=cmd_demo)
    args = p.parse_args()\n    return args.func(args)
if __name__=="__main__": raise SystemExit(main())