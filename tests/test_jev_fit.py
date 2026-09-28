"""The four-question JEV-fit table produced for every discovered decision."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import forge  # noqa: E402
import jev_fit  # noqa: E402

RECONSTRUCTION_MANIFEST = ROOT / "tests" / "fixtures" / "work-system-benchmark" / "manifest.yaml"


def _fit(project: Path) -> dict:
    return yaml.safe_load((project / "jev_fit.yaml").read_text(encoding="utf-8"))


def _by_id(document: dict) -> dict:
    return {row["decision_id"]: row for row in document["decisions"]}


class JevFitTests(unittest.TestCase):
    def test_every_cell_is_yes_no_or_unknown_with_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "scan"
            manifest = forge.scan_project(
                project=project,
                sources=[ROOT / "examples" / "cold-start-agent"],
                system_id="research_agent",
            )
            self.assertEqual(manifest["artifacts"]["jev_fit"], "jev_fit.md")
            document = _fit(project)
            self.assertTrue(document["decisions"])
            for row in document["decisions"]:
                for name in jev_fit.CRITERIA:
                    cell = row[name]
                    self.assertIn(cell["answer"], {"yes", "no", "unknown"})
                    self.assertTrue(cell["evidence"])
                    if cell["answer"] == "unknown":
                        self.assertTrue(cell["missing"])
            self.assertIn("| Decision | Bounded | Frequent | Painful | Measurable | Verdict |",
                          (project / "jev_fit.md").read_text(encoding="utf-8"))

    def test_cold_start_never_claims_workload_or_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "scan"
            forge.scan_project(
                project=project,
                sources=[ROOT / "examples" / "cold-start-agent"],
                system_id="research_agent",
            )
            rows = _by_id(_fit(project))
            for row in rows.values():
                self.assertEqual(row["frequent"]["answer"], "unknown")
                self.assertEqual(row["measurable"]["answer"], "unknown")
                self.assertNotEqual(row["verdict"], "jev_candidate")
            self.assertEqual(rows["choose_next_research_step"]["bounded"]["answer"], "yes")
            self.assertEqual(rows["draft_final_answer"]["verdict"], "not_bounded")
            self.assertEqual(rows["max_retries"]["verdict"], "keep_in_code")

    def test_case_discovery_uses_supplied_volume_cost_and_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "discover"
            fixture = ROOT / "examples" / "discovery-input"
            manifest = forge.discover_project(
                project=project,
                cases=fixture / "cases.jsonl",
                sources=[fixture / "sop.md"],
                system_id="shipment_triage",
                surface_field="decision_type",
                hourly_cost=45.0,
                monthly_volume=3000,
            )
            self.assertEqual(manifest["artifacts"]["jev_fit"], "jev_fit.md")
            row = _by_id(_fit(project))["shipment_exception"]
            self.assertEqual(row["bounded"]["answer"], "yes")
            self.assertEqual(row["frequent"]["answer"], "no")
            self.assertEqual(row["painful"]["answer"], "yes")
            self.assertEqual(row["measurable"]["answer"], "yes")
            self.assertEqual(row["verdict"], "jev_candidate")

    def test_missing_workload_inputs_stay_unknown_and_are_named(self):
        candidate = {
            "surface_id": "triage",
            "action_count": 3,
            "actions": [{"action_id": value} for value in ("a", "b", "c")],
            "case_count": 40,
            "outcome_coverage": 0.0,
            "value_estimate": {"estimated_monthly_volume": None, "estimated_monthly_review_hours": None},
        }
        row = jev_fit.assess_candidates([candidate], outcome_field=None)[0]
        self.assertEqual(row["frequent"]["answer"], "unknown")
        self.assertIn("--monthly-volume", row["frequent"]["missing"])
        self.assertEqual(row["painful"]["answer"], "unknown")
        self.assertEqual(row["measurable"]["answer"], "unknown")
        self.assertEqual(row["measurable"]["missing"], "--outcome-field")
        self.assertEqual(row["verdict"], "fill_gaps")

    def test_reconstruction_reads_outcome_links(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "reconstruct"
            manifest = forge.reconstruct_project(
                project=project,
                evidence_manifest=RECONSTRUCTION_MANIFEST,
                system_id="pydantic_ai_contribution_work",
            )
            self.assertEqual(manifest["artifacts"]["jev_fit"], "jev_fit.md")
            rows = _by_id(_fit(project))
            self.assertEqual(rows["human_review"]["measurable"]["answer"], "yes")
            self.assertEqual(rows["choose_next_actor"]["measurable"]["answer"], "unknown")
            self.assertTrue(all(row["bounded"]["answer"] == "yes" for row in rows.values()))


if __name__ == "__main__":
    unittest.main()
