**This round:** not ranked · Δ vs baseline -0.125 on 8 paired instances · 0 verified.

## Round `r0003` — `5FNENzASi4aamJmr1R7YRC2usvLvDd14q24YQYS2sgxAPNmT`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 8 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.1250 |
| standard error (incl. reference term) | 0.116927 |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** Δ -0.125 ± 0.117 does not clear zero at 90 % — Δc = 0, nothing to pay

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null p | canon p | Δc canon | label |
|---|---|---|---|---|---|
| `terminal_task` | 8 | 0.00 | 0.00 | -0.125 | frontier |

### Check the grading yourself

8 of 8 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`, and the commitment was published with the task. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (8)</summary>

```json
{
 "terminal-task-r0003-00": {
  "withheld": {
   "predicates": [
    [
     "custom",
     "facet_test",
     "test_state.py::test_final_summary_config_sanitization_summary"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_final_summary_seller_analytics_highlights"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_metrics_extract_keys"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_metrics_extract_top_three_products"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_metrics_extract_values_from_source"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_replacement_map_placeholder_format"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_replacement_map_reversibility"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_replacement_map_structure"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_sanitized_files_exist_and_use_placeholders[sanitized_path0-original_path0-settings.ini]"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_sanitized_files_exist_and_use_placeholders[sanitized_path1-original_path1-logging.yaml]"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_sanitized_files_preserve_non_secret_structure[sanitized_path0-original_path0]"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::test_sanitized_files_preserve_non_secret_structure[sanitized_path1-original_path1]"
    ]
   ]
  },
  "salt": "a14cb5e717a12111245f13ec244d84b6499fca9177bc3c4656ebe3c7f70d6a65"
 },
 "terminal-task-r0003-03": {
  "withheld": {
   "predicates": [
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_contains_presentation_content"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_contains_required_sections"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_contains_summary_table"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_contains_svg_content_summaries"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_exists_and_is_valid_package"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_font_and_formatting"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestProgressDocument::test_docx_has_page_numbers"
    ]
   ]
  },
  "salt": "684c2517cccb419eb702279c743b5c555b624680d42d9af888cdc50bc0742c0f"
 },
 "terminal-task-r0003-05": {
  "withheld": {
   "predicates": [
    [
     "custom",
     "facet_test",
     "test_state.py::TestFlightSearchSection::test_book_link_placeholder_present"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestFlightSearchSection::test_cheapest_connecting_flight_mentioned"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestHabitTrackerSection::test_habit_presence_in_listing"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestHabitTrackerSection::test_references_both_source_files"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestHabitTrackerSection::test_registration_confirmed"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestRSSServiceSection::test_port_4000_listening_confirmed"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestRSSServiceSection::test_port_4000_status_matches_log"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestReportStructure::test_required_headings_present_in_order"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestVideoProductionSection::test_combined_duration_present"
    ],
    [
     "custom",
     "facet_test",
     "test_state.py::TestVideoProductionSection::test_concatenatio
```

</details>