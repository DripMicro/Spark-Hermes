# Contributing

Two kinds of pull request are welcome.

**A strategy** — one directory under `submissions/<hotkey>/`, prose only, labelled `sh:strategy`. CI lints it
and nothing else runs from it. It is sealed into the next round, scored, and merged if crowned or closed with the
round otherwise. See [`submissions/README.md`](submissions/README.md).

**A change to the validator** — anything under `sh/`, `tests/` or `docs/`. Keep `ruff check`, `ruff format --check`,
`pyright` and `pytest` green; a behaviour change comes with the test that would have caught its absence. Anything
that alters what a round seals, grades or pays must also be recorded in `docs/pins.md`, since miners are measured
against it.

Never commit a withheld half, a salt, a token or a wallet. Task families and their withheld halves live in a private
repository on purpose; only what a round publishes belongs here.

Public code is MIT. Preserve the upstream licenses and notices of the pinned model and of
[Hermes Agent](https://github.com/NousResearch/hermes-agent); private control of a derived checkpoint grants no
rights over upstream weights or third-party data.
