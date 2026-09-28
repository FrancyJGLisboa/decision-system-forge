#!/usr/bin/env python3
"""Answer the four JEV-fit questions for every discovered decision.

Each decision gets one row with four criteria:

1. Bounded: the answer comes from a fixed set of options or a scale.
2. Frequent: it happens often enough (about 1,000 a day) or runs over a large archive.
3. Painful: a person does it by hand, or an LLM is too slow or expensive for it.
4. Measurable: a real outcome arrives later that the decision can be scored against.

Every cell is ``yes``, ``no`` or ``unknown`` with the evidence behind it and,
when the answer is not settled, the missing input that would settle it. Nothing
is inferred beyond the material the Forge already recorded: workload and outcome
questions stay ``unknown`` until someone supplies volumes, costs or outcomes.
The table is a triage aid. It grants no shadow eligibility or production authority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

CRITERIA = ("bounded", "frequent", "painful", "measurable")
DAILY_VOLUME_THRESHOLD = 1_000
MONTHLY_VOLUME_THRESHOLD = DAILY_VOLUME_THRESHOLD * 30
ARCHIVE_THRESHOLD = 10_000
PAIN_HOURS_THRESHOLD = 20.0
OUTCOME_COVERAGE_THRESHOLD = 0.5


def _cell(answer: str, evidence: str, missing: str | None = None) -> dict[str, Any]:
    return {"answer": answer, "evidence": evidence, "missing": missing}


def _verdict(cells: Mapping[str, Mapping[str, Any]], runtime: str | None = None) -> str:
    if runtime == "code":
        return "keep_in_code"
    if runtime == "llm" or cells["bounded"]["answer"] == "no":
        return "not_bounded"
    yes = sum(cells[name]["answer"] == "yes" for name in CRITERIA)
    unknown = sum(cells[name]["answer"] == "unknown" for name in CRITERIA)
    if yes >= 3:
        return "jev_candidate"
    if yes + unknown >= 3:
        return "fill_gaps"
    return "not_worth_jev"


def _row(
    decision_id: str,
    origin: str,
    cells: dict[str, dict[str, Any]],
    runtime: str | None = None,
) -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "origin": origin,
        **cells,
        "yes_count": sum(cells[name]["answer"] == "yes" for name in CRITERIA),
        "verdict": _verdict(cells, runtime),
    }


def _actions_text(actions: Iterable[Any], limit: int = 5) -> str:
    values = [str(value) for value in actions]
    shown = ", ".join(values[:limit])
    return shown + (f" (+{len(values) - limit} more)" if len(values) > limit else "")


def _source_ref(evidence: list[Mapping[str, Any]], locators: Mapping[str, str]) -> str:
    if not evidence:
        return "no cited source"
    first = evidence[0]
    locator = locators.get(str(first.get("source_id")), str(first.get("source_id")))
    return f"{Path(locator).name}:{first.get('line_start')}"


def assess_opportunities(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Rows for a cold-start scan: source-backed hypotheses with zero observed cases."""
    locators = {
        str(item["source_id"]): str(item.get("locator", item["source_id"]))
        for item in result.get("source_inventory") or []
    }
    rows = []
    for item in result.get("opportunities") or []:
        ref = _source_ref(item.get("evidence") or [], locators)
        actions = item.get("candidate_actions") or []
        kind = item.get("type")
        if kind == "open_generation":
            bounded = _cell("no", f"open text generation at {ref}")
        elif kind == "deterministic_rule":
            bounded = _cell("yes", f"exact comparison at {ref}; an ordinary code rule already decides it")
        elif len(actions) >= 2:
            bounded = _cell("yes", f"{len(actions)} options at {ref}: {_actions_text(actions)}")
        else:
            bounded = _cell("unknown", f"decision signal at {ref} without a closed option list",
                            "the complete list of options")
        actor = item.get("actor_type") or "unknown"
        if kind == "deterministic_rule":
            painful = _cell("no", "decided by an exact code rule, which is already fast and cheap")
        elif actor == "human":
            painful = _cell("yes", "a person makes this decision by hand")
        elif actor == "agent":
            painful = _cell("unknown", "an LLM or agent makes this decision today",
                            "LLM latency and cost per decision")
        else:
            painful = _cell("unknown", f"decision maker is recorded as {actor!r}",
                            "who makes this decision today and the time or cost per decision")
        cells = {
            "bounded": bounded,
            "frequent": _cell("unknown", "cold-start scan: 0 observed cases",
                              "decisions per day from logs, or a monthly volume estimate"),
            "painful": painful,
            "measurable": _cell("unknown", "no outcome source identified in the scanned material",
                                "where the eventual outcome of each decision is recorded"),
        }
        rows.append(_row(str(item["opportunity_id"]), "cold_start_scan", cells, item.get("recommended_runtime")))
    return rows


def assess_candidates(
    candidates: Iterable[Mapping[str, Any]],
    *,
    max_actions: int = 12,
    outcome_field: str | None = "outcome",
    review_minutes: float | None = None,
) -> list[dict[str, Any]]:
    """Rows for case-backed discovery surfaces (``decision_candidates.yaml``)."""
    rows = []
    for candidate in candidates:
        count = int(candidate.get("action_count") or 0)
        actions = [action.get("action_id") for action in candidate.get("actions") or []]
        if 2 <= count <= max_actions:
            bounded = _cell("yes", f"{count} observed actions: {_actions_text(actions)}")
        elif count < 2:
            bounded = _cell("no", f"only {count} observed action; nothing to choose between")
        else:
            bounded = _cell("no", f"{count} observed actions exceed the {max_actions}-action limit",
                            "a grouped or hierarchical option list")

        cases = int(candidate.get("case_count") or 0)
        value = candidate.get("value_estimate") or {}
        volume = value.get("estimated_monthly_volume")
        if volume is not None:
            answer = "yes" if volume >= MONTHLY_VOLUME_THRESHOLD else "no"
            frequent = _cell(answer, f"about {volume:,} decisions/month (~{volume / 30:,.0f}/day) "
                                     f"from the supplied monthly volume")
        elif cases >= ARCHIVE_THRESHOLD:
            frequent = _cell("yes", f"archive of {cases:,} resolved cases")
        else:
            frequent = _cell("unknown", f"{cases:,} resolved cases supplied; live volume not given",
                             "--monthly-volume")

        hours = value.get("estimated_monthly_review_hours")
        minutes = value.get("review_minutes_per_case", review_minutes)
        if hours is not None:
            labor = value.get("estimated_monthly_labor_value")
            money = f", about {labor:,.0f}/month in labor" if labor is not None else ""
            answer = "yes" if hours >= PAIN_HOURS_THRESHOLD else "no"
            painful = _cell(answer, f"about {hours:,} review hours/month at {minutes} min/case{money}")
        else:
            painful = _cell("unknown", "each case was resolved, but by whom and at what cost is not recorded",
                            "--monthly-volume (with --review-minutes and --hourly-cost)")

        coverage = float(candidate.get("outcome_coverage") or 0)
        if not outcome_field:
            measurable = _cell("unknown", "no outcome field was mapped", "--outcome-field")
        elif coverage >= OUTCOME_COVERAGE_THRESHOLD:
            measurable = _cell("yes", f"{coverage:.0%} of cases record an outcome in {outcome_field!r}")
        elif coverage == 0:
            measurable = _cell("no", f"no case records an outcome in {outcome_field!r}",
                               "a later outcome recorded per case")
        else:
            measurable = _cell("unknown", f"only {coverage:.0%} of cases record an outcome in {outcome_field!r}",
                               "outcomes for more cases")
        cells = {"bounded": bounded, "frequent": frequent, "painful": painful, "measurable": measurable}
        rows.append(_row(str(candidate["surface_id"]), "case_discovery", cells))
    return rows


def assess_reconstruction(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Rows for decisions in a reconstructed work system."""
    nodes = {node["node_id"]: node for node in result.get("nodes") or []}
    links = result.get("links") or []
    rows = []
    for candidate in result.get("decision_candidates") or []:
        node_id = candidate["node_id"]
        actions = candidate.get("candidate_actions") or []
        bounded = _cell("yes", f"{len(actions)} options: {_actions_text(actions)}")

        workflows = [item for item in result.get("workflows") or [] if node_id in (item.get("decisions") or [])]
        repeats = max((int(item.get("repeated_case_count") or 0) for item in workflows), default=0)
        if repeats >= ARCHIVE_THRESHOLD:
            frequent = _cell("yes", f"recurs in {repeats:,} observed cases")
        else:
            frequent = _cell("unknown", f"recurs in {repeats} observed public cases; live volume unknown",
                             "decisions per day from logs, or a monthly volume estimate")

        actors = sorted({
            str(nodes[actor].get("label"))
            for item in workflows
            for actor in item.get("actors") or []
            if actor in nodes
        })
        painful = _cell("unknown", f"actors in its workflows: {', '.join(actors) or 'none recorded'}",
                        "who decides and the time or cost per decision")

        outcome_links = [
            link for link in links
            if node_id in (link.get("from"), link.get("to"))
            and nodes.get(link["to"] if link.get("from") == node_id else link["from"], {}).get("kind") == "outcome"
        ]
        if outcome_links:
            link = outcome_links[0]
            target = link["to"] if link["from"] == node_id else link["from"]
            measurable = _cell("yes", f"{link.get('status')} link to outcome "
                                      f"{nodes[target].get('label')!r} ({link.get('relation')})")
        else:
            measurable = _cell("unknown", "no outcome linked to this decision in the reconstruction",
                               "where the eventual outcome of each decision is recorded")
        cells = {"bounded": bounded, "frequent": frequent, "painful": painful, "measurable": measurable}
        label = str(nodes.get(node_id, {}).get("label") or node_id)
        rows.append(_row(node_id, "work_system_reconstruction", cells) | {"label": label})
    return rows


VERDICT_TEXT = {
    "jev_candidate": "JEV candidate",
    "fill_gaps": "fill the gaps first",
    "not_worth_jev": "not worth JEV",
    "not_bounded": "not bounded: keep with an LLM or person",
    "keep_in_code": "keep in code",
}
VERDICT_ORDER = list(VERDICT_TEXT)


def document(system_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (VERDICT_ORDER.index(row["verdict"]), -row["yes_count"], row["decision_id"]))
    return {
        "schema_version": "1.0",
        "system_id": system_id,
        "criteria": {
            "bounded": "The answer comes from a fixed set of options or a scale.",
            "frequent": f"About {DAILY_VOLUME_THRESHOLD:,}+ decisions a day, or an archive of "
                        f"{ARCHIVE_THRESHOLD:,}+ cases.",
            "painful": f"A person does it by hand ({PAIN_HOURS_THRESHOLD:g}+ review hours/month), "
                       "or an LLM is too slow or expensive for it.",
            "measurable": f"A later outcome is recorded for at least {OUTCOME_COVERAGE_THRESHOLD:.0%} of cases.",
        },
        "rule": "Three or more yes answers make a JEV candidate.",
        "authority": "Triage only. It grants no shadow eligibility or production authority.",
        "decisions": ordered,
    }


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(doc: Mapping[str, Any]) -> str:
    rows = doc.get("decisions") or []
    lines = [
        "# JEV fit",
        "",
        f"System: `{doc.get('system_id')}`  ",
        f"Decisions: {len(rows)}",
        "",
        "Put a decision on JEV when at least 3 of the 4 answers are yes.",
        "",
    ]
    lines.extend(f"- **{name.capitalize()}:** {text}" for name, text in doc["criteria"].items())
    lines.append("")
    if not rows:
        lines.extend(["No decisions were discovered.", ""])
        return "\n".join(lines)
    lines.extend(
        [
            "| Decision | Bounded | Frequent | Painful | Measurable | Verdict |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        cells = " | ".join(row[name]["answer"] for name in CRITERIA)
        lines.append(f"| `{row['decision_id']}` | {cells} | {VERDICT_TEXT[row['verdict']]} ({row['yes_count']}/4) |")
    lines.extend(["", "## Evidence and missing inputs", ""])
    for row in rows:
        lines.extend([f"### `{row['decision_id']}`", ""])
        for name in CRITERIA:
            cell = row[name]
            text = f"- **{name.capitalize()}: {cell['answer']}**: {_escape(cell['evidence'])}"
            if cell.get("missing"):
                text += f". Needs: {_escape(cell['missing'])}"
            lines.append(text)
        lines.append("")
    lines.extend([str(doc["authority"]), ""])
    return "\n".join(lines)
