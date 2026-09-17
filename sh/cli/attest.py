"""The hotkey's signature over a submission — what binds a pull request to a miner and to a round.

    message   = "spark-hermes:" + repo + ":" + round_id + ":" + bundle_sha256 + ":" + signed_at
    signature = sr25519_sign(hotkey, message)

`attestation.json` sits at the bundle root, outside the digest and outside the prose rules. It names the hotkey
(the directory the bundle is submitted under), the round it was signed for, the digest it signed, when it was
signed (unix seconds), and the signature. The signing time is what makes "the miner's latest submission" well
defined: signed bundles are public, so without it anyone could reopen a miner's older bundle as a newer pull
request and have it counted instead. A validator accepts a PR only if all four agree with what it sees; a signature for another round or
another digest is worth nothing, so a bundle cannot be replayed into a later round or altered after signing.

The signing library is imported lazily: the lint runs in CI without it and reports the signature as unverified;
the seal always verifies.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

SCHEMA = "sh-attestation-v2"
FILE = "attestation.json"
DOMAIN = "gittensor-model-hub/Spark-Hermes"  # the competition the signature is for; a fork's rounds share nothing
SS58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{46,48}$")
ROUND = re.compile(r"^r\d{4}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def message(round_id: str, bundle_sha256: str, signed_at: int) -> bytes:
    return f"spark-hermes:{DOMAIN}:{round_id}:{bundle_sha256}:{int(signed_at)}".encode()


def available() -> bool:
    try:
        import substrateinterface  # noqa: F401
    except ImportError:
        return False
    return True


def load_keypair(source: str):
    """A keypair from a bittensor hotkey file (`secretSeed` or `secretPhrase`), a mnemonic, or a `//dev` URI."""
    from substrateinterface import Keypair, KeypairType

    if source.startswith("//"):  # a substrate dev URI (//Alice) — before the path heuristic, which `/` would trip
        return Keypair.create_from_uri(source, crypto_type=KeypairType.SR25519)
    p = Path(source).expanduser()
    looks_like_path = source.startswith((".", "/", "~")) or p.exists() or source.endswith((".json", ".txt"))
    if looks_like_path or " " not in source:  # a path, or a single token that is not a mnemonic
        if not p.is_file():
            raise ValueError(f"{source}: no such hotkey file (pass a --key that is a file, a mnemonic, or a //dev URI)")
        try:
            data = json.loads(p.read_text())
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError(
                f"{p}: not a bittensor hotkey file (expected JSON with secretSeed or secretPhrase). If this holds a "
                f"mnemonic, pass the words directly, not the file. [{exc}]"
            ) from exc
        if data.get("secretSeed"):
            return Keypair.create_from_seed(data["secretSeed"], crypto_type=KeypairType.SR25519)
        if data.get("secretPhrase"):
            return Keypair.create_from_mnemonic(data["secretPhrase"], crypto_type=KeypairType.SR25519)
        raise ValueError(
            f"{p}: a hotkey JSON with neither secretSeed nor secretPhrase (an encrypted key is not supported)"
        )
    return Keypair.create_from_mnemonic(source, crypto_type=KeypairType.SR25519)  # a mnemonic on the command line


def sign(keypair, round_id: str, bundle_sha256: str, signed_at: int | None = None) -> dict:
    """The attestation record for this keypair, round and digest, signed now (or at `signed_at`)."""
    at = int(time.time()) if signed_at is None else int(signed_at)
    sig = keypair.sign(message(round_id, bundle_sha256, at))
    return {
        "schema": SCHEMA,
        "hotkey": keypair.ss58_address,
        "round_id": round_id,
        "bundle_sha256": bundle_sha256,
        "signed_at": at,
        "signature": "0x" + sig.hex(),
    }


def verify(att: dict) -> bool:
    """True iff the signature is the hotkey's over this round and digest. Requires the library."""
    from substrateinterface import Keypair, KeypairType

    try:
        kp = Keypair(ss58_address=att["hotkey"], crypto_type=KeypairType.SR25519)
        return bool(kp.verify(message(att["round_id"], att["bundle_sha256"], att["signed_at"]), att["signature"]))
    except Exception:
        return False


def problems(att: dict | None, *, digest: str, hotkey: str | None = None, round_id: str | None = None) -> list[str]:
    """Structural and binding checks a lint can make without the library; the signature itself is checked only
    when the library is present. `hotkey`/`round_id`, when given, are what the record must name."""
    if att is None:
        return ["L10 attestation.json: missing — sign the bundle with your hotkey (python -m sh.cli.miner submit)"]
    out = []
    if att.get("schema") != SCHEMA:
        out.append(f"L10 attestation.json: schema {att.get('schema')!r} != {SCHEMA!r} — re-sign with the current CLI")
    if not isinstance(att.get("signed_at"), int) or isinstance(att.get("signed_at"), bool):
        out.append("L10 attestation.json: signed_at is not a unix time in whole seconds")
    if not SS58.match(str(att.get("hotkey", ""))):
        out.append("L10 attestation.json: hotkey is not an ss58 address")
    if not ROUND.match(str(att.get("round_id", ""))):
        out.append("L10 attestation.json: round_id is not r0000-style")
    if att.get("bundle_sha256") != digest:
        out.append("L10 attestation.json: bundle_sha256 does not match the bundle (re-sign after editing)")
    if hotkey and att.get("hotkey") != hotkey:
        out.append(f"L10 attestation.json: hotkey {att.get('hotkey')} != submission directory {hotkey}")
    if round_id and att.get("round_id") != round_id:
        out.append(f"L10 attestation.json: signed for {att.get('round_id')}, this round is {round_id}")
    if not out and available() and not verify(att):
        out.append("L10 attestation.json: signature is not the hotkey's over this round and digest")
    return out
