"""Exports: what leaves a closed round as training data, and what never does."""

from __future__ import annotations

from sh.exports.build import _secrets


def test_test_ids_of_a_withheld_suite_are_not_secrets_for_the_leak_scan():
    """A verified swe_fix trajectory names the tests it ran; those ids are public at close and part of any honest
    `pytest -v`. Only salts and withheld *values* are secrets."""
    reveal = {
        "t": {
            "salt": "a" * 64,
            "withheld": {
                "predicates": [
                    ["custom", "swe_test", "tests/text/test_fonts.py::DescribeFontFiles::it_catalogs"],
                    ["custom", "facet_test", "test_state.py::test_report_has_the_total"],
                    ["digest_is", "out.txt", "b" * 64],
                ]
            },
        }
    }
    assert _secrets(reveal) == {"a" * 64, "b" * 64}
