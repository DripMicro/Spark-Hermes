"""The hotkey's signature over a submission — what binds a pull request to a miner and to a round.

    message   = "spark-hermes:" + repo + ":" + round_id + ":" + bundle_sha256
    signature = sr25519_sign(hotkey, message)

`attestation.json` sits at the bundle root, outside the digest and outside the prose rules. It names the hotkey
(the directory the bundle is submitted under), the round it was signed for, the digest it signed, and the
signature. A validator accepts a PR only if all four agree with what it sees; a signature for another round or
another digest is worth nothing, so a bundle cannot be replayed into a later round or altered after signing.

The signing library is imported lazily: the lint runs in CI without it and reports the signature as unverified;
the seal always verifies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SCHEMA = "sh-attestation-v1"
FILE = "attestation.json"
DOMAIN = "gittensor-model-hub/Spark-Hermes"  # the competition the signature is for; a fork's rounds share nothing
SS58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{46,48}$")
ROUND = re.compile(r"^r\d{4}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def message(round_id: str, bundle_sha256: str) -> bytes:
    return f"spark-hermes:{DOMAIN}:{round_id}:{bundle_sha256}".encode()


def available() -> bool:
    try:
        import substrateinterface  # noqa: F401
    except ImportError:
        return False
    return True


def load_keypair(source: str):
    """A keypair from a bittensor hotkey file (`secretSeed` or `secretPhrase`), a mnemonic, or a `//dev` URI."""
    from substrateinterface import Keypair, KeypairType

    p = Path(source).expanduser()
    if p.is_file():
        data = json.loads(p.read_text())
        if data.get("secretSeed"):
            return Keypair.create_from_seed(data["secretSeed"], crypto_type=KeypairType.SR25519)
        if data.get("secretPhrase"):
            return Keypair.create_from_mnemonic(data["secretPhrase"], crypto_type=KeypairType.SR25519)
        raise ValueError(f"{p}: neither secretSeed nor secretPhrase")
    if source.startswith("//"):
        return Keypair.create_from_uri(source, crypto_type=KeypairType.SR25519)
    return Keypair.create_from_mnemonic(source, crypto_type=KeypairType.SR25519)


def sign(keypair, round_id: str, bundle_sha256: str) -> dict:
    """The attestation record for this keypair, round and digest."""
    sig = keypair.sign(message(round_id, bundle_sha256))
    return {
        "schema": SCHEMA,
        "hotkey": keypair.ss58_address,
        "round_id": round_id,
        "bundle_sha256": bundle_sha256,
        "signature": "0x" + sig.hex(),
    }


def verify(att: dict) -> bool:
    """True iff the signature is the hotkey's over this round and digest. Requires the library."""
    from substrateinterface import Keypair, KeypairType

    try:
        kp = Keypair(ss58_address=att["hotkey"], crypto_type=KeypairType.SR25519)
        return bool(kp.verify(message(att["round_id"], att["bundle_sha256"]), att["signature"]))
    except Exception:
        return False


def problems(att: dict | None, *, digest: str, hotkey: str | None = None, round_id: str | None = None) -> list[str]:
    """Structural and binding checks a lint can make without the library; the signature itself is checked only
    when the library is present. `hotkey`/`round_id`, when given, are what the record must name."""
    if att is None:
        return ["L10 attestation.json: missing — sign the bundle with your hotkey (python -m sh.cli.miner submit)"]
    out = []
    if att.get("schema") != SCHEMA:
        out.append(f"L10 attestation.json: schema {att.get('schema')!r} != {SCHEMA!r}")
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
