"""Mock miners for end-to-end testing: several personas, each with its own test keypair, submitting through the
same CLI a real miner uses — signed for the round, one PR per hotkey, replaced on resubmission.

    python -m sh.cli.mock_miners --miners DIR --keys DIR --round r0003 --checkout PATH

It is a test fixture and lives in `sh/cli` only because the miner CLI it drives lives there. Keys are generated
on first use under `--keys` and never leave the machine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sh.cli.miner import BRANCH, REPO, submit_bundle


def keypair_for(keys: Path, persona: str):
    """The persona's keypair, created on first use and kept as a mnemonic file."""
    from substrateinterface import Keypair, KeypairType

    keys.mkdir(parents=True, exist_ok=True)
    f = keys / f"{persona}.json"
    if not f.exists():
        mnemonic = Keypair.generate_mnemonic()
        kp = Keypair.create_from_mnemonic(mnemonic, crypto_type=KeypairType.SR25519)
        f.write_text(json.dumps({"persona": persona, "secretPhrase": mnemonic, "ss58Address": kp.ss58_address}))
        f.chmod(0o600)
    data = json.loads(f.read_text())
    return Keypair.create_from_mnemonic(data["secretPhrase"], crypto_type=KeypairType.SR25519)


def open_prs(miners: Path, keys: Path, repo: str, base: str, checkout: Path, round_id: str) -> dict:
    """Submit every persona's bundle for `round_id`. Returns {persona: result}."""
    out = {}
    for bundle in sorted(p for p in miners.iterdir() if p.is_dir()):
        kp = keypair_for(keys, bundle.name)
        r = submit_bundle(bundle, kp, round_id=round_id, repo=repo, base=base, checkout=checkout)
        out[bundle.name] = {k: v for k, v in r.items() if k in ("ok", "hotkey", "pr", "created", "skipped", "problems")}
        if not r["ok"]:
            print(f"{bundle.name}: not submitted: {r['problems'][0]}", file=sys.stderr)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--miners", required=True)
    ap.add_argument("--keys", required=True)
    ap.add_argument("--round", required=True)
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--base", default=BRANCH)
    ap.add_argument("--checkout", required=True)
    a = ap.parse_args(argv)
    print(json.dumps(open_prs(Path(a.miners), Path(a.keys), a.repo, a.base, Path(a.checkout), a.round), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
