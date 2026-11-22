import json
import subprocess
import sys
from pathlib import Path

import pytest

from bod_evidence_envelope import EvidenceEnvelopeError, create_evidence_envelope
from bod_portable import (
    LEGACY_SNAPSHOT_DOMAIN,
    LEGACY_SNAPSHOT_SCHEMA,
    SNAPSHOT_DOMAIN,
    SNAPSHOT_SCHEMA,
    canonical_json,
    create_evidence_bundle,
    create_portable_checkpoint,
    extract_evidence_bundle,
    parse_portable,
    repository_snapshot,
    sha256_bytes,
    verify_evidence_bundle,
    verify_portable_chain,
    verify_portable_graph,
    verify_snapshot,
)


def test_capture_verify_recover_cli(tmp_path):
    artifact = tmp_path / "checkpoint.json"
    capture = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "capture", ".", "--project", "bod-test", "--out", str(artifact)],
        capture_output=True, text=True, check=False,
    )
    assert capture.returncode == 0, capture.stdout + capture.stderr
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable"],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    recover = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "recover", str(artifact)],
        capture_output=True, text=True, check=False,
    )
    assert recover.returncode == 0, recover.stdout + recover.stderr
    assert json.loads(recover.stdout)["status"] == "RECOVERY_VERIFIED"


def test_portable_checkpoint_binds_snapshot_and_envelope():
    snapshot = repository_snapshot(Path("."))
    envelope = create_evidence_envelope(
        project_id="p", protocol_version="0.1", state_root=snapshot["state_root"],
        predecessor_state_root=None, transition_id="t", evidence=(), capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    parse_portable(checkpoint)
    checkpoint["snapshot"]["files"][0]["size"] += 1
    with pytest.raises(EvidenceEnvelopeError):
        parse_portable(checkpoint)


def test_cli_rejects_mutation(tmp_path):
    artifact = tmp_path / "checkpoint.json"
    subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "capture", ".", "--project", "bod-test", "--out", str(artifact)],
        check=True,
    )
    value = json.loads(artifact.read_text())
    value["envelope"]["transition_id"] = "tampered"
    artifact.write_text(json.dumps(value))
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable"],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode != 0


def test_snapshot_rejects_unsafe_paths_and_noncanonical_entries():
    snapshot = repository_snapshot(Path("."))
    unsafe = json.loads(json.dumps(snapshot))
    unsafe["files"][0]["path"] = "../outside"
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(unsafe)

    boolean_size = json.loads(json.dumps(snapshot))
    boolean_size["files"][0]["size"] = True
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(boolean_size)

    unsorted = json.loads(json.dumps(snapshot))
    unsorted["files"] = list(reversed(unsorted["files"]))
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(unsorted)


def test_snapshot_hashes_symlink_target_not_external_file_contents(tmp_path):
    import hashlib
    import os

    repository = tmp_path / "repository"
    repository.mkdir()
    external_file = tmp_path / "outside.txt"
    external_file.write_text("external payload must not be read", encoding="utf-8")
    link = repository / "linked.txt"
    link.symlink_to(external_file)

    subprocess.run(["git", "-C", str(repository), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repository), "add", "--", "linked.txt"], check=True, capture_output=True)

    snapshot = repository_snapshot(repository)
    entry = snapshot["files"][0]
    link_target = os.fsencode(os.readlink(link))

    assert entry["path"] == "linked.txt"
    assert entry["sha256"] == hashlib.sha256(link_target).hexdigest()
    assert entry["size"] == len(link_target)
    assert entry["mode"] == 0o120000
    assert entry["sha256"] != hashlib.sha256(external_file.read_bytes()).hexdigest()


def test_snapshot_commits_to_executable_bit(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    script = repository / "run.sh"
    script.write_text("#!/bin/sh\necho BOD\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repository), "add", "--", "run.sh"], check=True, capture_output=True)

    before = repository_snapshot(repository)
    assert before["files"][0]["mode"] == 0o100644
    script.chmod(0o645)  # Git ignores group/other execute bits when deriving 100644/100755.
    group_other_executable = repository_snapshot(repository)
    assert group_other_executable["state_root"] == before["state_root"]
    script.chmod(0o755)
    after = repository_snapshot(repository)

    assert after["files"][0]["mode"] == 0o100755
    assert before["state_root"] != after["state_root"]
    verify_snapshot(before)
    verify_snapshot(after)


def test_snapshot_rejects_invalid_git_file_mode():
    snapshot = repository_snapshot(Path("."))
    invalid = json.loads(json.dumps(snapshot))
    invalid["files"][0]["mode"] = True
    with pytest.raises(EvidenceEnvelopeError, match="file mode"):
        verify_snapshot(invalid)


def test_snapshot_v0_1_remains_verifiable():
    files = [{"path": "legacy.txt", "sha256": sha256_bytes(b"legacy"), "size": 6}]
    durable = {"schema": LEGACY_SNAPSHOT_SCHEMA, "files": files}
    legacy = {
        **durable,
        "state_root": sha256_bytes(LEGACY_SNAPSHOT_DOMAIN + canonical_json(durable)),
    }
    verify_snapshot(legacy)


def test_independent_verifier_accepts_legacy_snapshot_checkpoint(tmp_path):
    files = [{"path": "legacy.txt", "sha256": sha256_bytes(b"legacy"), "size": 6}]
    durable = {"schema": LEGACY_SNAPSHOT_SCHEMA, "files": files}
    legacy = {
        **durable,
        "state_root": sha256_bytes(LEGACY_SNAPSHOT_DOMAIN + canonical_json(durable)),
    }
    envelope = create_evidence_envelope(
        project_id="legacy-project", protocol_version="0.1", state_root=legacy["state_root"],
        predecessor_state_root=None, transition_id="legacy-genesis", evidence=(), capture_boundary="legacy-fixture",
    )
    checkpoint = create_portable_checkpoint(snapshot=legacy, envelope=envelope)
    artifact = tmp_path / "legacy-checkpoint.json"
    artifact.write_text(json.dumps(checkpoint), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(artifact)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "VALID_INTEGRITY"


def _synthetic_snapshot(label: str) -> dict:
    files = [{"path": "state.txt", "sha256": sha256_bytes(label.encode()), "size": len(label), "mode": 0o100644}]
    durable = {"schema": SNAPSHOT_SCHEMA, "files": files}
    return {**durable, "state_root": sha256_bytes(SNAPSHOT_DOMAIN + canonical_json(durable))}


def test_portable_graph_verifies_forks_and_independent_cli(tmp_path):
    from bod_evidence_envelope import create_evidence_envelope

    snapshots = [_synthetic_snapshot(name) for name in ("genesis", "branch-b", "branch-c")]
    genesis = create_evidence_envelope(
        project_id="graph-project", protocol_version="0.1", state_root=snapshots[0]["state_root"],
        predecessor_state_root=None, transition_id="genesis", evidence=(), capture_boundary="test",
    )
    children = [
        create_evidence_envelope(
            project_id="graph-project", protocol_version="0.1", state_root=snapshot["state_root"],
            predecessor_state_root=snapshots[0]["state_root"], transition_id=f"branch-{index}",
            evidence=(), capture_boundary="test",
        )
        for index, snapshot in enumerate(snapshots[1:], start=1)
    ]
    checkpoints = [
        create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
        for snapshot, envelope in [(snapshots[0], genesis), *zip(snapshots[1:], children)]
    ]

    graph = verify_portable_graph(checkpoints)
    assert graph["fork_points"] == (snapshots[0]["state_root"],)
    assert set(graph["heads"]) == {snapshot["state_root"] for snapshot in snapshots[1:]}
    with pytest.raises(EvidenceEnvelopeError, match="verify it as a graph"):
        verify_portable_chain(checkpoints)

    artifact = tmp_path / "forked-checkpoints.json"
    artifact.write_text(json.dumps({"checkpoints": checkpoints}), encoding="utf-8")
    independent = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(artifact), "--graph"],
        capture_output=True, text=True, check=False,
    )
    assert independent.returncode == 0, independent.stdout + independent.stderr
    assert json.loads(independent.stdout)["status"] == "VALID_INTEGRITY"

    cli = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable", "--graph"],
        capture_output=True, text=True, check=False,
    )
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert json.loads(cli.stdout)["canonical_head"] is None


def test_self_contained_evidence_bundle_round_trip_and_tamper_detection(tmp_path):
    import hashlib

    from bod_evidence_envelope import EvidenceReferenceV0_1

    payload = b'{"predicateType":"https://slsa.dev/provenance/v1","subject":[]}'
    digest = hashlib.sha256(payload).hexdigest()
    snapshot = _synthetic_snapshot("bundle-state")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="slsa-provenance",
            digest=digest,
            media_type="application/vnd.in-toto+json",
            uri="../../outside-file",
            issuer="test-issuer",
        )],
        capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    bundle = create_evidence_bundle(checkpoint=checkpoint, payloads={digest: payload})
    extracted_dir = tmp_path / "extracted"
    extracted = extract_evidence_bundle(bundle, extracted_dir)
    assert extracted["status"] == "BUNDLE_EXTRACTED"
    assert (extracted_dir / f"{digest}.json").read_bytes() == payload
    manifest = json.loads((extracted_dir / "manifest.json").read_text())
    assert manifest["objects"][0]["digest"] == f"sha256:{digest}"
    assert manifest["objects"][0]["evidence_type"] == "slsa-provenance"
    assert manifest["objects"][0]["uri"] == "../../outside-file"
    assert manifest["objects"][0]["file"] == f"{digest}.json"
    assert not (tmp_path / "outside-file").exists()
    with pytest.raises(EvidenceEnvelopeError, match="output directory already exists"):
        extract_evidence_bundle(bundle, extracted_dir)
    assert (extracted_dir / f"{digest}.json").read_bytes() == payload

    result = verify_evidence_bundle(bundle)
    assert result["payloads_complete"] is True
    assert result["evidence_objects"] == 1
    assert result["payload_bytes"] == len(payload)
    assert result["semantic_truth"] == "NOT_ASSERTED"
    assert result["bundle_authenticity"] == "NOT_ASSERTED"

    tampered = json.loads(json.dumps(bundle))
    tampered["objects"][0]["data_base64"] = "eA=="
    # Recompute outer commitment to exercise payload-level digest validation.
    from bod_portable import BUNDLE_DOMAIN
    tampered["bundle_id"] = sha256_bytes(BUNDLE_DOMAIN + canonical_json({
        "schema": tampered["schema"],
        "checkpoint": tampered["checkpoint"],
        "objects": tampered["objects"],
    }))
    rejected_dir = tmp_path / "tampered-extraction"
    with pytest.raises(EvidenceEnvelopeError, match="size mismatch|digest mismatch"):
        extract_evidence_bundle(tampered, rejected_dir)
    assert not rejected_dir.exists()
    with pytest.raises(EvidenceEnvelopeError, match="size mismatch|digest mismatch"):
        verify_evidence_bundle(tampered)


def test_bundle_extract_uses_jsonl_extension_for_ndjson_payload(tmp_path):
    from bod_evidence_envelope import EvidenceReferenceV0_1

    payload = b'{"type":"attestation"}\n'
    digest = sha256_bytes(payload)
    snapshot = _synthetic_snapshot("bundle-jsonl")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-jsonl",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="attestation-bundle", digest=digest,
            media_type="application/x-ndjson",
        )],
        capture_boundary="test",
    )
    bundle = create_evidence_bundle(
        checkpoint=create_portable_checkpoint(snapshot=snapshot, envelope=envelope),
        payloads={digest: payload},
    )
    output = tmp_path / "jsonl-recovered"
    extract_evidence_bundle(bundle, output)
    assert (output / f"{digest}.jsonl").read_bytes() == payload


def test_bundle_extract_uses_asc_extension_for_pgp_key_payload(tmp_path):
    from bod_evidence_envelope import EvidenceReferenceV0_1

    payload = b"-----BEGIN PGP PUBLIC KEY BLOCK-----\nfixture\n"
    digest = sha256_bytes(payload)
    snapshot = _synthetic_snapshot("bundle-pgp")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-pgp",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="release-signing-key", digest=digest,
            media_type="application/pgp-keys",
        )],
        capture_boundary="test",
    )
    bundle = create_evidence_bundle(
        checkpoint=create_portable_checkpoint(snapshot=snapshot, envelope=envelope),
        payloads={digest: payload},
    )
    output = tmp_path / "pgp-recovered"
    extract_evidence_bundle(bundle, output)
    assert (output / f"{digest}.asc").read_bytes() == payload


def test_self_contained_evidence_bundle_requires_every_referenced_payload():
    from bod_evidence_envelope import EvidenceReferenceV0_1
    payload = b"missing evidence"
    digest = sha256_bytes(payload)
    snapshot = _synthetic_snapshot("missing-payload")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="test-report", digest=digest, media_type="text/plain",
        )],
        capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    with pytest.raises(EvidenceEnvelopeError, match="payload set must exactly match"):
        create_evidence_bundle(checkpoint=checkpoint, payloads={})


def test_bundle_cli_round_trip(tmp_path):
    import hashlib

    from bod_evidence_envelope import EvidenceReferenceV0_1
    payload = b"fixture evidence"
    digest = hashlib.sha256(payload).hexdigest()
    payload_path = tmp_path / "evidence.json"
    payload_path.write_bytes(payload)
    snapshot = _synthetic_snapshot("bundle-cli")
    envelope = create_evidence_envelope(
        project_id="bundle-cli", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="test-fixture", digest=digest, media_type="application/json",
        )],
        capture_boundary="test",
    )
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(create_portable_checkpoint(snapshot=snapshot, envelope=envelope)))
    bundle_path = tmp_path / "bundle.json"
    create = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "bundle-create", str(checkpoint_path),
         "--payload", f"{digest}={payload_path}", "--out", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert create.returncode == 0, create.stdout + create.stderr
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "bundle-verify", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    extracted_dir = tmp_path / "bundle-extracted"
    extract = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "bundle-extract", str(bundle_path),
         "--out-dir", str(extracted_dir)],
        capture_output=True, text=True, check=False,
    )
    assert extract.returncode == 0, extract.stdout + extract.stderr
    assert json.loads(extract.stdout)["status"] == "BUNDLE_EXTRACTED"
    assert (extracted_dir / f"{digest}.json").read_bytes() == payload

    independent = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert independent.returncode == 0, independent.stdout + independent.stderr
    assert json.loads(independent.stdout)["status"] == "VALID_SELF_CONTAINED_BUNDLE"


def test_evidence_inspector_validates_slsa_and_cyclonedx_structure():
    from bod_evidence_formats import inspect_evidence_payload

    slsa = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "release.tar.gz", "digest": {"sha256": "a" * 64}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://example.invalid/buildtype/v1",
                "externalParameters": {"ref": "refs/tags/v1"},
            },
            "runDetails": {"builder": {"id": "https://example.invalid/builder"}},
        },
    }
    result = inspect_evidence_payload(json.dumps(slsa).encode())
    assert result["format"] == "slsa-provenance-v1"
    assert result["structure"] == "VALID"
    assert result["signature_verification"] == "NOT_PERFORMED"

    cyclonedx = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "version": 1,
        "components": [{"type": "library", "name": "example", "version": "1.0"}],
    }
    result = inspect_evidence_payload(json.dumps(cyclonedx).encode())
    assert result["format"] == "cyclonedx-json"
    assert result["component_count"] == 1


def test_evidence_inspector_validates_spdx_23_and_dsse_wrapper():
    import base64

    from bod_evidence_formats import inspect_evidence_payload

    spdx = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "example SBOM",
        "documentNamespace": "https://example.invalid/spdx/123",
        "creationInfo": {
            "created": "2026-11-22T00:00:00Z",
            "creators": ["Tool: fixture-1.0"],
        },
        "packages": [],
    }
    result = inspect_evidence_payload(json.dumps(spdx).encode())
    assert result["format"] == "spdx-json-2"
    assert result["package_count"] == 0

    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://example.invalid/predicate/v1",
        "predicate": {},
    }
    dsse = {
        "payloadType": "application/vnd.in-toto+json",
        "payload": base64.b64encode(json.dumps(statement).encode()).decode(),
        "signatures": [{"keyid": "fixture-key", "sig": base64.b64encode(b"signature").decode()}],
    }
    result = inspect_evidence_payload(json.dumps(dsse).encode())
    assert result["format"] == "in-toto-statement-v1"
    assert result["dsse_signature_count"] == 1
    assert result["signature_verification"] == "NOT_PERFORMED"


def test_evidence_inspector_rejects_malformed_slsa_and_invalid_spdx():
    import pytest

    from bod_evidence_formats import EvidenceFormatError, inspect_evidence_payload

    malformed_slsa = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://example.invalid/buildtype/v1",
                "externalParameters": {},
            },
            "runDetails": {"builder": {}},
        },
    }
    with pytest.raises(EvidenceFormatError, match="builder.id"):
        inspect_evidence_payload(json.dumps(malformed_slsa).encode())

    invalid_spdx = {"spdxVersion": "SPDX-2.3"}
    with pytest.raises(EvidenceFormatError, match="dataLicense"):
        inspect_evidence_payload(json.dumps(invalid_spdx).encode())


def test_evidence_inspector_cli(tmp_path):
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "components": [],
    }
    evidence_path = tmp_path / "bom.json"
    evidence_path.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "evidence-inspect", str(evidence_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["structure"] == "VALID"


def test_sigstore_github_verification_command_is_delegated_without_shell(monkeypatch):
    from types import SimpleNamespace

    import bod_evidence_formats as formats

    captured = {}
    monkeypatch.setattr(formats.shutil if hasattr(formats, "shutil") else __import__("shutil"),
                        "which", lambda name: "/usr/bin/sigstore")
    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="OK: artifact", stderr="")
    monkeypatch.setattr(formats.subprocess if hasattr(formats, "subprocess") else __import__("subprocess"),
                        "run", fake_run)
    result = formats.run_sigstore_verification(
        mode="github",
        subject="/tmp/artifact.bin",
        bundle="/tmp/artifact.bundle.json",
        offline=True,
        cert_identity="https://github.com/org/repo/.github/workflows/ci.yml@refs/heads/main",
        trigger="push",
        sha="a" * 40,
        workflow_name="CI",
        repository="org/repo",
        ref="refs/heads/main",
    )
    assert result["status"] == "VALID"
    assert result["signature_verification"] == "VALID"
    assert "--offline" in captured["command"]
    assert captured["kwargs"]["shell"] is False
    assert captured["kwargs"]["timeout"] == 120


def test_sigstore_verification_rejects_missing_policy_and_missing_binary(monkeypatch):
    import shutil

    import pytest

    import bod_evidence_formats as formats

    with pytest.raises(formats.EvidenceVerificationError, match="requires"):
        formats.run_sigstore_verification(
            mode="github", subject="sha256:" + "a" * 64, bundle="bundle.json"
        )
    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(formats.EvidenceVerificationError, match="not found"):
        formats.run_sigstore_verification(
            mode="identity",
            subject="sha256:" + "a" * 64,
            bundle="bundle.json",
            cert_identity="builder",
            cert_oidc_issuer="https://issuer.example",
        )


def test_sigstore_identity_verification_uses_explicit_issuer(monkeypatch):
    import shutil
    import subprocess
    from types import SimpleNamespace

    import bod_evidence_formats as formats

    captured = {}
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/sigstore")
    def fake_run(command, **kwargs):
        captured["command"] = command
        return SimpleNamespace(returncode=1, stdout="", stderr="identity mismatch")
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = formats.run_sigstore_verification(
        mode="identity",
        subject="sha256:" + "a" * 64,
        bundle="bundle.json",
        cert_identity="release@example.org",
        cert_oidc_issuer="https://accounts.example.org",
    )
    assert result["status"] == "INVALID"
    assert "--cert-oidc-issuer" in captured["command"]
    assert "https://accounts.example.org" in captured["command"]
