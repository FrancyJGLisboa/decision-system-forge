#!/usr/bin/env python3
"""Product entry point for cold-start scan and discovery-to-shadow workflows.

The individual compiler scripts remain available for development and audits.
This module is the stable user-facing lifecycle: create a project, explain the
best supported candidate, record a domain review, and measure it in shadow mode.
No command in this V1 executes a discovered action.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discover_decision_system as discovery  # noqa: E402
import evaluate_discovered_system as discovered_eval  # noqa: E402
import observe_decision_events as event_observation  # noqa: E402
import acquire_work_system_evidence as evidence_acquisition  # noqa: E402
import reconstruct_work_system as work_reconstruction  # noqa: E402
import scan_decision_opportunities as opportunity_scan  # noqa: E402
import integration_package  # noqa: E402
import jev_fit  # noqa: E402
import binding_verification  # noqa: E402
import shadow_controller  # noqa: E402
import jev_shadow_transport  # noqa: E402
import product_lifecycle as lifecycle_contract  # noqa: E402
from transports import laya_transport  # noqa: E402


PRODUCT_VERSION = "0.9.0"
LIFECYCLE_FILE = Path(__file__).resolve().parents[1] / "product_lifecycle.yaml"
PROJECT_FILE = "forge_project.yaml"
REVIEW_FILE = "review.md"
SCAN_REVIEW_FILE = "scan_review.md"
OPPORTUNITY_MAP_FILE = "decision_opportunity_map.yaml"
OBSERVATION_PLAN_FILE = "observation_plan.yaml"
INSTRUMENTATION_SPEC_FILE = "instrumentation_spec.yaml"
EVENT_SCHEMA_FILE = "event_schema.json"
DECISION_SYSTEM_MAP_FILE = "decision_system_map.yaml"
OBSERVATION_MANIFEST_FILE = "evidence/observation_manifest.yaml"
SHADOW_REVIEW_FILE = "shadow_review.yaml"
WORK_SYSTEM_MAP_FILE = "work_system_map.yaml"
WORK_SYSTEM_REVIEW_FILE = "work_system_review.md"
EVIDENCE_MANIFEST_FILE = "evidence_manifest.yaml"
SOURCE_CATALOG_FILE = "evidence/source_catalog.yaml"
RECONSTRUCTION_REQUEST_FILE = "reconstruction_request.md"
WORK_SYSTEM_PROPOSAL_FILE = "work_system_proposal.yaml"
JEV_FIT_FILE = "jev_fit.yaml"
JEV_FIT_REVIEW_FILE = "jev_fit.md"


class ProductStateError(RuntimeError):
    """The requested product transition is invalid or unsafe."""


def load_lifecycle() -> dict[str, Any]:
    """Load the single product-facing lifecycle contract."""
    try:
        return lifecycle_contract.load_contract(LIFECYCLE_FILE)
    except lifecycle_contract.LifecycleError as exc:
        raise ProductStateError(f"product lifecycle contract is invalid: {exc}") from exc


def inspect_project(project: str | Path) -> dict[str, Any]:
    """Combine persisted evidence with canonical, non-authorizing guidance."""
    root = Path(project).expanduser().resolve()
    manifest = load_project(root)
    try:
        guidance = lifecycle_contract.guidance_for(load_lifecycle(), manifest, root)
    except lifecycle_contract.LifecycleError as exc:
        raise ProductStateError(f"project violates the canonical lifecycle: {exc}") from exc
    return {
        "project": manifest,
        "guidance": guidance,
        "authority": {
            "executes_actions": False,
            "production": False,
            "approval_automated": False,
        },
    }


def render_next_action(project: str | Path) -> str:
    inspection = inspect_project(project)
    guidance = inspection["guidance"]
    inputs = ", ".join(guidance["required_inputs"]) or "none"
    lines = [
        f"Stage `{guidance['stage']}`.",
        f"Next action: `{guidance['action_id']}`.",
        str(guidance["summary"]),
        f"Required input: {inputs}.",
    ]
    if guidance.get("command"):
        lines.append(f"Command: {guidance['command']}")
    else:
        lines.append("No command is run automatically at this evidence or human-review gate.")
    lines.append("This guidance does not grant execution authority and does not mutate the project.")
    return "\n".join(lines)


def start_project(
    *, project: Path, system_id: str, repositories: list[str], urls: list[str], sources: list[Path],
    cases: Path | None = None, taxonomy: Path | None = None, scope: str | None = None,
    case_id_field: str = "case_id", text_field: str = "message",
    action_field: str = "resolved_action", outcome_field: str | None = "outcome",
    surface_field: str | None = None, review_minutes: float = 2.0,
    hourly_cost: float | None = None, monthly_volume: int | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Route the simple public entry point to an existing proven compiler."""
    if cases is not None:
        if repositories or urls:
            raise ProductStateError(
                "--repo and --url would be ignored by resolved-case discovery; acquire them first or pass local --source snapshots"
            )
        result = discover_project(
            project=project, cases=cases, sources=sources, taxonomy=taxonomy,
            system_id=system_id, scope=scope, case_id_field=case_id_field, text_field=text_field,
            action_field=action_field, outcome_field=outcome_field, surface_field=surface_field,
            review_minutes=review_minutes, hourly_cost=hourly_cost,
            monthly_volume=monthly_volume, force=force,
        )
        _validate_project_document(result)
        return result
    if not (repositories or urls or sources):
        raise ProductStateError("start requires at least one --repo, --url, --source, or --cases input")
    result = acquire_reconstruction_project(
        project=project, system_id=system_id, repositories=repositories, urls=urls,
        sources=sources, max_files=evidence_acquisition.DEFAULT_MAX_FILES,
        max_source_bytes=evidence_acquisition.DEFAULT_MAX_SOURCE_BYTES, force=force,
    )
    _validate_project_document(result)
    return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ProductStateError(f"cannot read project file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductStateError(f"project file {path} must contain a mapping")
    return value


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _validate_project_document(document: Mapping[str, Any]) -> None:
    try:
        errors = lifecycle_contract.validate_manifest(load_lifecycle(), document)
    except lifecycle_contract.LifecycleError as exc:
        raise ProductStateError(f"product lifecycle validation failed: {exc}") from exc
    if errors:
        raise ProductStateError(f"project violates the canonical lifecycle: {errors[0]}")


def _write_project(
    root: Path,
    document: dict[str, Any],
    *,
    before_stage: str | None = None,
    via: str | None = None,
) -> None:
    """Validate every product manifest and, for updates, its canonical transition."""
    _validate_project_document(document)
    if before_stage is not None:
        after_stage = str(document.get("stage"))
        if not via or not lifecycle_contract.transition_allowed(
            load_lifecycle(), before_stage, after_stage, via
        ):
            raise ProductStateError(
                f"canonical lifecycle forbids transition {before_stage!r} -> {after_stage!r} via {via!r}"
            )
    _write_yaml(root / PROJECT_FILE, document)


def _verify_external_transition(
    project: str | Path,
    *,
    before_stage: str,
    via: str,
) -> dict[str, Any]:
    after = load_project(project)
    if not lifecycle_contract.transition_allowed(
        load_lifecycle(), before_stage, str(after.get("stage")), via
    ):
        raise ProductStateError(
            f"canonical lifecycle forbids transition {before_stage!r} -> {after.get('stage')!r} via {via!r}"
        )
    return after


def _existing_project_stage(project: str | Path) -> str | None:
    root = Path(project).expanduser().resolve()
    if not (root / PROJECT_FILE).is_file():
        return None
    return str(load_project(root)["stage"])


def _write_jev_fit(root: Path, system_id: str, rows: list[dict[str, Any]]) -> None:
    document = jev_fit.document(system_id, rows)
    _write_yaml(root / JEV_FIT_FILE, document)
    (root / JEV_FIT_REVIEW_FILE).write_text(jev_fit.render_markdown(document), encoding="utf-8")


def _load_candidates(discovery_dir: Path) -> list[dict[str, Any]]:
    document = _yaml(discovery_dir / "decision_candidates.yaml")
    candidates = document.get("candidates") or []
    if not isinstance(candidates, list) or not all(isinstance(item, dict) for item in candidates):
        raise ProductStateError("discovery output contains an invalid candidate list")
    return candidates


def _percent(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "n/a"
    return f"{value:.1%}"


def _render_review(
    *,
    system_id: str,
    cases: int,
    candidates: list[dict[str, Any]],
    selected_surface: str | None,
) -> str:
    lines = [
        "# Forge V1 review",
        "",
        f"System: `{system_id}`  ",
        f"Resolved cases analyzed: {cases}  ",
        "",
        "This review describes observed historical behavior. It does not grant production authority.",
        "",
        "## Ranked decision surfaces",
        "",
        "| Rank | Surface | Priority | Evidence readiness | Cases | Actions | Local holdout |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, candidate in enumerate(candidates, 1):
        baseline = candidate.get("baseline") or {}
        lines.append(
            f"| {rank} | `{candidate.get('surface_id')}` | "
            f"{float(candidate.get('priority_score', 0)):.1f} | "
            f"{float(candidate.get('readiness_score', 0)):.1f} | "
            f"{candidate.get('case_count', 0)} | {candidate.get('action_count', 0)} | "
            f"{_percent(baseline.get('accuracy'))} |"
        )

    if selected_surface is None:
        lines.extend(
            [
                "",
                "## No candidate passed the evidence gate",
                "",
                "The Forge did not compile a decision system. Blocking gaps:",
                "",
            ]
        )
        gaps = [
            gap
            for candidate in candidates
            for gap in candidate.get("blocking_gaps", [])
            if isinstance(gap, str)
        ]
        lines.extend(f"- {gap}" for gap in gaps or ["No bounded surface had enough evidence."])
        lines.extend(
            [
                "",
                "Add representative resolved cases or correct the case-field mapping, then run discovery again.",
                "",
            ]
        )
        return "\n".join(lines)

    selected = next(item for item in candidates if item.get("surface_id") == selected_surface)
    lines.extend(
        [
            "",
            "## Recommended candidate",
            "",
            f"Surface: `{selected_surface}`  ",
            f"Status: `{selected.get('status')}`  ",
            f"Cases: {selected.get('case_count')}  ",
            "",
            "Observed choices:",
            "",
        ]
    )
    for action in selected.get("actions", []):
        lines.append(f"- `{action.get('action_id')}` - observed in {action.get('case_count', 0)} cases")
    value = selected.get("value_estimate") or {}
    if value.get("estimated_monthly_review_hours") is not None:
        lines.extend(
            [
                "",
                "Estimated workload represented by this surface:",
                "",
                f"- {value['estimated_monthly_review_hours']} review hours/month",
                f"- {value.get('estimated_monthly_volume')} cases/month",
                "- This is a workload estimate, not promised savings.",
            ]
        )
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "- Shadow mode executes no actions.",
            "- Historical actions do not prove legality or correctness.",
            "- The compiled candidate has no inferred executable bindings.",
            "- Production requires verified policy, bindings, trusted labels, calibration, and a release gate.",
            "",
            "## Decision required",
            "",
            "A named domain owner must confirm that the vocabulary and historical labels are suitable for non-executing shadow evaluation.",
            "",
        ]
    )
    return "\n".join(lines)


def load_project(project: str | Path) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    document = _yaml(root / PROJECT_FILE)
    if document.get("schema_version") != "1.0":
        raise ProductStateError("unsupported Forge project schema")
    _validate_project_document(document)
    return document


def _render_scan_review(result: Mapping[str, Any]) -> str:
    opportunities = result.get("opportunities") or []
    lines = [
        "# Forge cold-start review",
        "",
        f"System: `{result.get('system_id')}`  ",
        "Resolved cases: 0  ",
        f"Sources inventoried: {len(result.get('source_inventory') or [])}  ",
        f"Decision opportunities: {len(opportunities)}",
        "",
        "This scan contains source-backed hypotheses only. It is not eligible for shadow evaluation.",
        "",
    ]
    if not opportunities:
        lines.extend(
            [
                "## No decision signals found",
                "",
                "Add operational code, tool schemas, interfaces, SOPs, traces, or a System 2 proposal with exact source citations.",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            "## Opportunity map",
            "",
            "| Opportunity | Type | Actor | Recommended runtime | Actions |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in opportunities:
        actions = ", ".join(f"`{value}`" for value in item.get("candidate_actions", [])) or "-"
        lines.append(
            f"| `{item['opportunity_id']}` | {item['type']} | {item['actor_type']} | "
            f"{item['recommended_runtime']} | {actions} |"
        )
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "- Every item has maturity `hypothesis` and zero observed cases.",
            "- No executable binding was inferred or generated.",
            "- Bounded semantic candidates must be instrumented before JEV evaluation.",
            "- A reviewed JEV surface must add an explicit safe no-match or fallback action.",
            "- Open generation stays with an LLM; exact rules stay in code.",
            "",
            "## Next decision",
            "",
            "Select one bounded semantic candidate for instrumentation, or provide more operational material.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_work_system_review(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forge work-system reconstruction",
        "",
        f"System: `{result.get('system_id')}`  ",
        f"Sources: {len(result.get('source_inventory') or [])}  ",
        f"Actors, artifacts, states, activities, decisions, and outcomes: {len(result.get('nodes') or [])}  ",
        "",
        "This is an evidence-backed reconstruction, not a claim that the complete true system was recovered.",
        "",
        "## Reconstructed workflows",
        "",
    ]
    for workflow in result.get("workflows") or []:
        lines.extend(
            [
                f"### {workflow.get('label')}",
                "",
                " → ".join(f"`{step}`" for step in workflow.get("steps") or []),
                "",
                f"Evidence forms: {', '.join(workflow.get('source_kinds') or [])}  ",
                f"Repeated public cases: {workflow.get('repeated_case_count')}  ",
                f"Recurrence: `{workflow.get('recurrence_status')}`",
                "",
                "Known gaps:",
                "",
            ]
        )
        lines.extend(f"- {gap}" for gap in workflow.get("gaps") or [])
        lines.append("")
    lines.extend(["## Bounded decision candidates", ""])
    decisions_by_id = {
        node["node_id"]: node
        for node in result.get("nodes") or []
        if node.get("kind") == "decision"
    }
    for candidate in result.get("decision_candidates") or []:
        node = decisions_by_id[candidate["node_id"]]
        actions = ", ".join(f"`{action}`" for action in candidate.get("candidate_actions") or [])
        lines.append(
            f"- **{node.get('label')}** — {actions}; maturity `{candidate.get('maturity')}`; shadow eligible: no."
        )
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "- Declared behavior remains distinct from observed behavior.",
            "- System 2 links are accepted only when their quoted evidence exists.",
            "- No decision candidate is automatically eligible for JEV shadow evaluation.",
            "- The reconstruction executes no action and grants no production authority.",
            "",
            "## Next action",
            "",
            "Review the reconstructed workflows, then select a bounded decision for observation or provide evidence that closes a named gap.",
            "",
        ]
    )
    return "\n".join(lines)


def reconstruct_project(
    *,
    project: str | Path,
    evidence_manifest: str | Path,
    system_id: str,
    force: bool = False,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    evidence_path = Path(evidence_manifest).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ProductStateError(f"project path exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()) and not force:
        raise ProductStateError(f"project directory is not empty: {root}; use --force to refresh generated artifacts")
    source_document = work_reconstruction.load_yaml(evidence_path)
    systems = source_document.get("systems") or []
    system = next(
        (item for item in systems if isinstance(item, Mapping) and item.get("system_id") == system_id),
        None,
    )
    if system is None:
        raise ProductStateError(f"system {system_id!r} is not present in the evidence manifest")
    result = work_reconstruction.reconstruct(system, root=evidence_path.parent)
    root.mkdir(parents=True, exist_ok=True)
    _write_yaml(root / WORK_SYSTEM_MAP_FILE, result)
    (root / WORK_SYSTEM_REVIEW_FILE).write_text(_render_work_system_review(result), encoding="utf-8")
    _write_jev_fit(root, str(result["system_id"]), jev_fit.assess_reconstruction(result))
    created_at = _now()
    manifest = {
        "schema_version": "1.0",
        "product_version": PRODUCT_VERSION,
        "system_id": result["system_id"],
        "created_at": created_at,
        "updated_at": created_at,
        "stage": "work_system_mapped",
        "next_action": "review_decision_opportunities",
        "selected_surface": None,
        "selected_opportunity": None,
        "summary": {
            "sources": len(result["source_inventory"]),
            "nodes": len(result["nodes"]),
            "links": len(result["links"]),
            "workflows": len(result["workflows"]),
            "decision_candidates": len(result["decision_candidates"]),
            "evidence_gaps": len(result["gaps"]),
        },
        "artifacts": {
            "work_system_map": WORK_SYSTEM_MAP_FILE,
            "work_system_review": WORK_SYSTEM_REVIEW_FILE,
            "jev_fit": JEV_FIT_REVIEW_FILE,
            "candidate_bundle": None,
        },
        "evidence_manifest": {
            "locator": str(evidence_path),
            "sha256": work_reconstruction.sha256_file(evidence_path),
        },
        "safety": dict(result["safety"]),
    }
    _write_project(root, manifest)
    return manifest


def acquire_reconstruction_project(
    *,
    project: str | Path,
    system_id: str,
    repositories: list[str] | None = None,
    urls: list[str] | None = None,
    sources: list[str | Path] | None = None,
    max_files: int = evidence_acquisition.DEFAULT_MAX_FILES,
    max_source_bytes: int = evidence_acquisition.DEFAULT_MAX_SOURCE_BYTES,
    force: bool = False,
    url_fetcher: evidence_acquisition.UrlFetcher | None = None,
    repository_materializer: evidence_acquisition.RepositoryMaterializer | None = None,
) -> dict[str, Any]:
    """Acquire direct inputs and prepare a bounded System 2 reconstruction task."""
    root = Path(project).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ProductStateError(f"project path exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()) and not force:
        raise ProductStateError(f"project directory is not empty: {root}; use --force to refresh generated artifacts")
    root.mkdir(parents=True, exist_ok=True)
    acquired = evidence_acquisition.acquire(
        project=root,
        system_id=system_id,
        repositories=repositories or [],
        urls=urls or [],
        sources=sources or [],
        max_files=max_files,
        max_source_bytes=max_source_bytes,
        url_fetcher=url_fetcher,
        repository_materializer=repository_materializer,
    )
    catalog = acquired["catalog"]
    created_at = _now()
    manifest = {
        "schema_version": "1.0",
        "product_version": PRODUCT_VERSION,
        "system_id": system_id,
        "created_at": created_at,
        "updated_at": created_at,
        "stage": "evidence_inventoried",
        "next_action": "complete_system2_reconstruction",
        "selected_surface": None,
        "selected_opportunity": None,
        "summary": {
            "sources": catalog["included_count"],
            "skipped_sources": catalog["skipped_count"],
            "repositories": len(catalog["repositories"]),
            "source_kinds": sorted({item["kind"] for item in catalog["sources"]}),
        },
        "artifacts": {
            "evidence_manifest": EVIDENCE_MANIFEST_FILE,
            "source_catalog": SOURCE_CATALOG_FILE,
            "reconstruction_request": RECONSTRUCTION_REQUEST_FILE,
            "work_system_proposal": WORK_SYSTEM_PROPOSAL_FILE,
            "work_system_map": None,
            "work_system_review": None,
            "candidate_bundle": None,
        },
        "evidence_manifest": {
            "locator": EVIDENCE_MANIFEST_FILE,
            "sha256": work_reconstruction.sha256_file(root / EVIDENCE_MANIFEST_FILE),
        },
        "safety": {
            "descriptive_only": True,
            "system2_proposals_validated": False,
            "inference_is_authority": False,
            "executes_actions": False,
            "production_authority": False,
            "shadow_eligible": False,
            "raw_source_content_persisted": True,
        },
    }
    _write_project(root, manifest)
    return manifest


def finalize_acquired_reconstruction(
    *,
    project: str | Path,
    proposal: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a System 2 proposal and finalize an acquired project in place."""
    root = Path(project).expanduser().resolve()
    manifest = load_project(root)
    if manifest.get("stage") != "evidence_inventoried":
        raise ProductStateError(
            "direct reconstruction can only be finalized from stage 'evidence_inventoried'"
        )
    evidence_path = root / EVIDENCE_MANIFEST_FILE
    evidence_document = work_reconstruction.load_yaml(evidence_path)
    systems = evidence_document.get("systems") or []
    system = next(
        (
            item
            for item in systems
            if isinstance(item, Mapping) and item.get("system_id") == manifest.get("system_id")
        ),
        None,
    )
    if system is None or system.get("provenance_mode") != "acquired":
        raise ProductStateError("project does not contain an acquired evidence system")

    target = root / WORK_SYSTEM_PROPOSAL_FILE
    supplied = Path(proposal).expanduser().resolve() if proposal is not None else target
    if not supplied.is_file():
        raise ProductStateError(f"System 2 proposal does not exist: {supplied}")
    proposal_document = work_reconstruction.load_yaml(supplied)
    if supplied != target:
        _write_yaml(target, proposal_document)
    system["proposal_file"] = WORK_SYSTEM_PROPOSAL_FILE
    system["proposal_sha256"] = work_reconstruction.sha256_file(target)
    _write_yaml(evidence_path, evidence_document)

    result = work_reconstruction.reconstruct(system, root=root)
    _write_yaml(root / WORK_SYSTEM_MAP_FILE, result)
    (root / WORK_SYSTEM_REVIEW_FILE).write_text(_render_work_system_review(result), encoding="utf-8")
    _write_jev_fit(root, str(result["system_id"]), jev_fit.assess_reconstruction(result))
    manifest["updated_at"] = _now()
    manifest["stage"] = "work_system_mapped"
    manifest["next_action"] = "review_decision_opportunities"
    manifest["summary"] = {
        "sources": len(result["source_inventory"]),
        "nodes": len(result["nodes"]),
        "links": len(result["links"]),
        "workflows": len(result["workflows"]),
        "decision_candidates": len(result["decision_candidates"]),
        "evidence_gaps": len(result["gaps"]),
    }
    manifest["artifacts"]["work_system_map"] = WORK_SYSTEM_MAP_FILE
    manifest["artifacts"]["work_system_review"] = WORK_SYSTEM_REVIEW_FILE
    manifest["artifacts"]["jev_fit"] = JEV_FIT_REVIEW_FILE
    manifest["evidence_manifest"]["sha256"] = work_reconstruction.sha256_file(evidence_path)
    manifest["safety"] = dict(result["safety"]) | {"raw_source_content_persisted": True}
    _write_project(root, manifest, before_stage="evidence_inventoried", via="reconstruct --proposal")
    return manifest


def prepare_integration(project: str | Path, *, decision_id: str | None = None, force: bool = False) -> dict[str, Any]:
    """Compile a non-executing integration contract from a mapped work system."""
    before_stage = _existing_project_stage(project)
    result = integration_package.compile_package(project=project, decision_id=decision_id, force=force)
    if before_stage is not None:
        _verify_external_transition(project, before_stage=before_stage, via="prepare-integration")
    return result


def propose_bindings(project: str | Path, *, proposal: str | Path) -> dict[str, Any]:
    """Validate agent-authored binding candidates without invoking their targets."""
    before_stage = _existing_project_stage(project)
    result = binding_verification.propose_bindings(project=project, proposal=proposal)
    if before_stage is not None:
        _verify_external_transition(project, before_stage=before_stage, via="propose-bindings")
    return result


def verify_bindings(project: str | Path, *, observations: str | Path) -> dict[str, Any]:
    """Promote runtime-observed candidates to non-executing shadow evidence."""
    before_stage = _existing_project_stage(project)
    result = binding_verification.verify_bindings(project=project, observations=observations)
    if before_stage is not None:
        _verify_external_transition(project, before_stage=before_stage, via="verify-bindings")
    return result


def prepare_controller(project: str | Path, *, proposal: str | Path) -> dict[str, Any]:
    """Compile reviewed state and legality policy into a non-executing controller."""
    before_stage = _existing_project_stage(project)
    result = shadow_controller.prepare_controller(project=project, proposal=proposal)
    if before_stage is not None:
        _verify_external_transition(project, before_stage=before_stage, via="prepare-controller")
    return result


def run_controller_shadow(
    project: str | Path,
    *,
    observations: str | Path,
    model: str = jev_shadow_transport.DEFAULT_MODEL,
    endpoint: str | None = None,
    timeout: float = 30.0,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run the reviewed finite controller against TypeSafe JEV without executing actions."""
    before_stage = _existing_project_stage(project)
    result = jev_shadow_transport.run_controller_shadow(
        project,
        observations=observations,
        model=model,
        endpoint=endpoint,
        timeout=timeout,
        run_id=run_id,
    )
    if before_stage is not None:
        _verify_external_transition(project, before_stage=before_stage, via="run-controller-shadow")
    return result


def _observation_plan(result: Mapping[str, Any]) -> dict[str, Any]:
    plans = []
    for item in result.get("opportunities") or []:
        if item.get("type") != "bounded_semantic_decision":
            continue
        plans.append(
            {
                "opportunity_id": item["opportunity_id"],
                "status": "needs_observation",
                "actor_type": item["actor_type"],
                "candidate_actions": item.get("candidate_actions", []),
                "capture": [
                    "state_before",
                    "available_actions",
                    "selected_action",
                    "actor_type",
                    "state_after",
                    "eventual_outcome",
                ],
                "next_action": "instrument",
                "limitations": [
                    "Do not capture private reasoning or chain-of-thought.",
                    "Capture only observable state and structured decision outcomes.",
                    "Add a reviewed safe no-match or fallback before compiling a JEV Choice.",
                ],
            }
        )
    return {
        "schema_version": "1.0",
        "system_id": result["system_id"],
        "event_contract": {
            "schema_version": "1.0",
            "required_fields": [
                "event_id",
                "case_id",
                "opportunity_id",
                "occurred_at",
                "actor_type",
                "state_before",
                "available_actions",
                "selected_action",
                "state_after",
                "source_ref",
            ],
            "optional_fields": ["confidence", "eventual_outcome", "outcome_observed_at"],
            "temporal_rule": "Context must contain only information available at occurred_at.",
        },
        "plans": plans,
        "safety": {
            "executes_actions": False,
            "captures_chain_of_thought": False,
            "shadow_eligible": False,
        },
    }


def scan_project(
    *,
    project: str | Path,
    sources: list[str | Path],
    system_id: str,
    proposals: list[Mapping[str, Any]] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ProductStateError(f"project path exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()) and not force:
        raise ProductStateError(f"project directory is not empty: {root}; use --force to refresh generated artifacts")
    root.mkdir(parents=True, exist_ok=True)
    result = opportunity_scan.scan(sources, system_id=system_id, proposals=proposals)
    opportunities = result["opportunities"]
    stage = "hypotheses_ready" if opportunities else "no_opportunities"
    next_action = "select_candidate_for_instrumentation" if opportunities else "add_operational_material"
    created_at = _now()
    manifest = {
        "schema_version": "1.0",
        "product_version": PRODUCT_VERSION,
        "system_id": result["system_id"],
        "created_at": created_at,
        "updated_at": created_at,
        "stage": stage,
        "next_action": next_action,
        "selected_surface": None,
        "selected_opportunity": None,
        "summary": {
            "observed_cases": 0,
            "sources": len(result["source_inventory"]),
            "opportunities": len(opportunities),
            "bounded_semantic_candidates": sum(
                item["type"] == "bounded_semantic_decision" for item in opportunities
            ),
        },
        "artifacts": {
            "scan_review": SCAN_REVIEW_FILE,
            "opportunity_map": OPPORTUNITY_MAP_FILE,
            "observation_plan": OBSERVATION_PLAN_FILE,
            "jev_fit": JEV_FIT_REVIEW_FILE,
            "source_inventory": "evidence/source_inventory.yaml",
            "candidate_bundle": None,
        },
        "safety": {
            "hypotheses_only": True,
            "shadow_eligible": False,
            "executes_actions": False,
            "production_authority": False,
            "bindings_generated": False,
            "raw_source_content_persisted": False,
        },
    }
    opportunity_map = {key: value for key, value in result.items() if key != "source_inventory"}
    _write_yaml(root / OPPORTUNITY_MAP_FILE, opportunity_map)
    _write_yaml(
        root / "evidence" / "source_inventory.yaml",
        {
            "schema_version": "1.0",
            "system_id": result["system_id"],
            "sources": result["source_inventory"],
        },
    )
    _write_yaml(root / OBSERVATION_PLAN_FILE, _observation_plan(result))
    (root / SCAN_REVIEW_FILE).write_text(_render_scan_review(result), encoding="utf-8")
    _write_jev_fit(root, str(result["system_id"]), jev_fit.assess_opportunities(result))
    _write_project(root, manifest)
    return manifest


def select_opportunity(
    project: str | Path,
    *,
    opportunity_id: str,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manifest = load_project(root)
    before_stage = str(manifest.get("stage"))
    if manifest.get("stage") != "hypotheses_ready":
        raise ProductStateError(
            f"project is not ready for hypothesis selection; current stage is {manifest.get('stage')!r}"
        )
    opportunity_map = _yaml(root / OPPORTUNITY_MAP_FILE)
    opportunities = opportunity_map.get("opportunities") or []
    selected = next(
        (
            item
            for item in opportunities
            if isinstance(item, Mapping) and item.get("opportunity_id") == opportunity_id
        ),
        None,
    )
    if selected is None:
        raise ProductStateError(f"opportunity {opportunity_id!r} does not exist in this project")
    if selected.get("type") != "bounded_semantic_decision":
        raise ProductStateError(
            f"opportunity {opportunity_id!r} is not a bounded semantic decision and should not be instrumented for JEV"
        )
    actions = selected.get("candidate_actions") or []
    if not isinstance(actions, list) or len(actions) < 2:
        raise ProductStateError(f"opportunity {opportunity_id!r} has no bounded action vocabulary")

    observation_plan = _yaml(root / OBSERVATION_PLAN_FILE)
    event_contract = observation_plan.get("event_contract")
    if not isinstance(event_contract, Mapping):
        raise ProductStateError("observation plan is missing its event contract")
    source_inventory = (_yaml(root / "evidence" / "source_inventory.yaml").get("sources") or [])
    sources_by_id = {
        item.get("source_id"): item for item in source_inventory if isinstance(item, Mapping)
    }
    capture_points = []
    for evidence in selected.get("evidence", []):
        if not isinstance(evidence, Mapping):
            continue
        source = sources_by_id.get(evidence.get("source_id"))
        if not source:
            continue
        locator = str(source.get("locator", ""))
        suffix = Path(locator).suffix.lower()
        kind = evidence.get("kind")
        if kind not in {"bounded_choice_call", "bounded_transition_label"}:
            continue
        if suffix in {".ts", ".tsx"} and kind == "bounded_choice_call":
            description = "Record the bounded choice result immediately after this call, before side effects."
        elif suffix == ".dot" and kind == "bounded_transition_label":
            description = "Record the selected labelled transition at the graph dispatcher, before executing its target."
        else:
            description = "Record the bounded decision immediately after selection and before side effects."
        capture_points.append(
            {
                "source_id": source.get("source_id"),
                "locator": locator,
                "line_start": evidence.get("line_start"),
                "line_end": evidence.get("line_end"),
                "description": description,
                "review_required": True,
            }
        )
    specification = {
        "schema_version": "1.0",
        "system_id": manifest["system_id"],
        "status": "selected_for_observation",
        "opportunity": {
            "opportunity_id": selected["opportunity_id"],
            "type": selected["type"],
            "actor_type": selected.get("actor_type", "unknown"),
            "candidate_actions": actions,
            "evidence": selected.get("evidence", []),
        },
        "event_contract": dict(event_contract),
        "integration": {
            "format": "jsonl",
            "schema": EVENT_SCHEMA_FILE,
            "capture_point": "Immediately after a choice is made and before its side effects run.",
            "raw_event_destination": "outside_forge_project",
            "suggested_capture_points": capture_points,
            "scaffold_status": "review_required_not_generated",
        },
        "safety": {
            "observation_only": True,
            "captures_chain_of_thought": False,
            "modifies_source_application": False,
            "calls_jev": False,
            "executes_actions": False,
        },
    }
    _write_yaml(root / INSTRUMENTATION_SPEC_FILE, specification)
    _write_json(root / EVENT_SCHEMA_FILE, event_observation.event_schema(selected))
    manifest["stage"] = "instrumentation_ready"
    manifest["next_action"] = "collect_observations"
    manifest["selected_opportunity"] = selected["opportunity_id"]
    manifest["updated_at"] = _now()
    manifest["artifacts"]["instrumentation_spec"] = INSTRUMENTATION_SPEC_FILE
    manifest["artifacts"]["event_schema"] = EVENT_SCHEMA_FILE
    _write_project(root, manifest, before_stage=before_stage, via="select")
    return manifest


def observe_project(
    project: str | Path,
    *,
    events: str | Path,
    minimum_events: int = 3,
    minimum_path_cases: int = 2,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    event_source = Path(events).expanduser().resolve()
    if event_source == root or root in event_source.parents:
        raise ProductStateError(
            "raw event sources must remain outside the Forge project; move the JSONL log and retry"
        )
    manifest = load_project(root)
    before_stage = str(manifest.get("stage"))
    allowed_stages = {"instrumentation_ready", "observations_collected", "workflow_map_ready"}
    if manifest.get("stage") not in allowed_stages:
        raise ProductStateError(
            f"project is not ready to observe events; current stage is {manifest.get('stage')!r}"
        )
    specification = _yaml(root / INSTRUMENTATION_SPEC_FILE)
    opportunity = specification.get("opportunity")
    if not isinstance(opportunity, Mapping):
        raise ProductStateError("instrumentation specification is missing the selected opportunity")
    if opportunity.get("opportunity_id") != manifest.get("selected_opportunity"):
        raise ProductStateError("instrumentation specification does not match the selected opportunity")

    result = event_observation.observe(
        event_source,
        opportunity,
        system_id=manifest["system_id"],
        minimum_events=minimum_events,
        minimum_path_cases=minimum_path_cases,
    )
    decision_map = result["decision_system_map"]
    observation_manifest = result["observation_manifest"]
    _write_yaml(root / DECISION_SYSTEM_MAP_FILE, decision_map)
    _write_yaml(root / OBSERVATION_MANIFEST_FILE, observation_manifest)
    ready = bool(decision_map["readiness"]["workflow_map_ready"])
    manifest["stage"] = "workflow_map_ready" if ready else "observations_collected"
    manifest["next_action"] = (
        "review_decision_system_map" if ready else "collect_more_observations"
    )
    manifest["updated_at"] = _now()
    manifest["observations"] = observation_manifest["summary"]
    manifest["artifacts"]["decision_system_map"] = DECISION_SYSTEM_MAP_FILE
    manifest["artifacts"]["observation_manifest"] = OBSERVATION_MANIFEST_FILE
    manifest["safety"]["raw_event_state_persisted"] = False
    manifest["safety"]["workflow_map_descriptive_only"] = True
    _write_project(root, manifest, before_stage=before_stage, via="observe")
    return manifest


def discover_project(
    *,
    project: str | Path,
    cases: str | Path,
    sources: list[str | Path],
    system_id: str,
    scope: str | None = None,
    taxonomy: str | Path | None = None,
    case_id_field: str = "case_id",
    text_field: str = "message",
    action_field: str = "resolved_action",
    outcome_field: str | None = "outcome",
    surface_field: str | None = None,
    min_cases: int = 20,
    min_action_cases: int = 3,
    max_actions: int = 12,
    test_fraction: float = 0.2,
    confidence_threshold: float = 0.8,
    review_minutes: float = 2.0,
    hourly_cost: float | None = None,
    monthly_volume: int | None = None,
    force: bool = False,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ProductStateError(f"project path exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()) and not force:
        raise ProductStateError(f"project directory is not empty: {root}; use --force to refresh generated artifacts")
    root.mkdir(parents=True, exist_ok=True)
    discovery_dir = root / "discovery"
    source_paths = [Path(item) for item in sources]
    taxonomy_path = Path(taxonomy) if taxonomy is not None else None
    if taxonomy_path is not None and taxonomy_path not in source_paths:
        source_paths.append(taxonomy_path)
    arguments = argparse.Namespace(
        cases=Path(cases),
        source=source_paths,
        taxonomy=taxonomy_path,
        output=discovery_dir,
        system_id=system_id,
        scope=scope,
        case_id_field=case_id_field,
        text_field=text_field,
        action_field=action_field,
        outcome_field=outcome_field,
        surface_field=surface_field,
        min_cases=min_cases,
        min_action_cases=min_action_cases,
        max_actions=max_actions,
        test_fraction=test_fraction,
        confidence_threshold=confidence_threshold,
        review_minutes=review_minutes,
        hourly_cost=hourly_cost,
        monthly_volume=monthly_volume,
        force=force,
    )
    result = discovery.discover(arguments)
    candidates = _load_candidates(discovery_dir)
    selected = next(
        (item for item in candidates if item.get("status") == "candidate_for_human_review"),
        None,
    )
    selected_surface = str(selected["surface_id"]) if selected else None
    stage = "awaiting_review" if selected_surface else "insufficient_evidence"
    next_action = "review_candidate" if selected_surface else "add_evidence_and_rediscover"
    created_at = _now()
    manifest = {
        "schema_version": "1.0",
        "product_version": PRODUCT_VERSION,
        "system_id": discovery.slug(system_id, fallback="discovered_system"),
        "created_at": created_at,
        "updated_at": created_at,
        "stage": stage,
        "next_action": next_action,
        "selected_surface": selected_surface,
        "summary": {
            "cases": result["cases"],
            "sources": result["sources"],
            "candidates": result["candidates"],
            "eligible": result["eligible"],
        },
        "artifacts": {
            "review": REVIEW_FILE,
            "jev_fit": JEV_FIT_REVIEW_FILE,
            "discovery": "discovery",
            "candidate_bundle": "discovery/candidate_bundle" if selected_surface else None,
        },
        "safety": {
            "executes_actions": False,
            "production_authority": False,
            "raw_case_context_persisted": False,
        },
    }
    _write_project(root, manifest)
    _write_jev_fit(
        root,
        manifest["system_id"],
        jev_fit.assess_candidates(
            candidates,
            max_actions=max_actions,
            outcome_field=outcome_field,
            review_minutes=review_minutes,
        ),
    )
    (root / REVIEW_FILE).write_text(
        _render_review(
            system_id=manifest["system_id"],
            cases=result["cases"],
            candidates=candidates,
            selected_surface=selected_surface,
        ),
        encoding="utf-8",
    )
    return manifest


def approve_for_shadow(
    project: str | Path,
    *,
    surface_id: str,
    reviewer: str,
    notes: str | None = None,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manifest = load_project(root)
    before_stage = str(manifest.get("stage"))
    if manifest.get("stage") != "awaiting_review":
        raise ProductStateError(f"project is not awaiting review; current stage is {manifest.get('stage')!r}")
    if surface_id != manifest.get("selected_surface"):
        raise ProductStateError(
            f"surface {surface_id!r} is not the compiled candidate {manifest.get('selected_surface')!r}"
        )
    reviewer = reviewer.strip()
    if not reviewer:
        raise ProductStateError("a named reviewer is required before the candidate can be approved for shadow")
    record = {
        "schema_version": "1.0",
        "system_id": manifest["system_id"],
        "surface_id": surface_id,
        "reviewer": reviewer,
        "reviewed_at": _now(),
        "notes": notes or "",
        "approval": {
            "vocabulary_and_historical_labels_reviewed": True,
            "shadow_only": True,
            "production_authority": False,
            "action_legality_verified": False,
            "bindings_verified": False,
        },
        "limitations": [
            "This approval permits non-executing evaluation only.",
            "Historical labels remain observational until independently verified.",
        ],
    }
    _write_yaml(root / SHADOW_REVIEW_FILE, record)
    manifest["stage"] = "ready_for_shadow"
    manifest["next_action"] = "run_shadow"
    manifest["updated_at"] = _now()
    manifest["artifacts"]["shadow_review"] = SHADOW_REVIEW_FILE
    _write_project(root, manifest, before_stage=before_stage, via="approve-shadow")
    return manifest


def run_shadow(
    project: str | Path,
    *,
    transport: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    provider: str = "typesafe",
    endpoint: str | None = None,
    timeout: float = 30.0,
    label_source: str = "historical",
    model: str | None = None,
) -> dict[str, Any]:
    root = Path(project).expanduser().resolve()
    manifest = load_project(root)
    before_stage = str(manifest.get("stage"))
    if manifest.get("stage") != "ready_for_shadow":
        raise ProductStateError("candidate must be approved for shadow by a named domain owner before evaluation")
    review = _yaml(root / SHADOW_REVIEW_FILE)
    approval = review.get("approval") or {}
    if not approval.get("shadow_only") or approval.get("production_authority"):
        raise ProductStateError("shadow review record is missing the non-production safety boundary")
    if transport is None:
        if provider == "laya":
            transport = laya_transport(model or "laya:typed-decisions")
        elif provider == "typesafe":
            transport = discovered_eval.typesafe_transport(endpoint, None, timeout)
        else:
            raise ProductStateError(f"unsupported provider {provider!r}")
    measured = discovered_eval.evaluate(
        root / "discovery",
        transport=transport,
        label_source=label_source,
        model=model,
    )
    manifest["stage"] = "shadow_measured"
    manifest["updated_at"] = _now()
    manifest["next_action"] = (
        "calibrate_and_run_release_gate"
        if measured.get("release_gate_eligible")
        else "verify_labels_and_calibrate"
    )
    manifest["shadow"] = {
        key: measured.get(key)
        for key in (
            "status",
            "surface_id",
            "question_id",
            "holdout_cases",
            "raw_accuracy",
            "confidence_threshold",
            "confident_coverage",
            "confident_accuracy",
            "illegal_answers",
            "label_source",
            "release_gate_eligible",
            "release_status",
            "note",
        )
    }
    manifest["artifacts"]["shadow_log"] = "discovery/jev_holdout_log.jsonl"
    manifest["artifacts"]["shadow_metrics"] = "discovery/jev_performance.json"
    _write_project(root, manifest, before_stage=before_stage, via="shadow")
    return manifest


def render_status(project: str | Path) -> str:
    manifest = load_project(project)
    stage = str(manifest.get("stage", "unknown")).replace("_", " ").upper()
    lines = [
        f"FORGE PROJECT: {manifest.get('system_id')}",
        f"STAGE: {stage}",
        f"NEXT: {manifest.get('next_action')}",
    ]
    if manifest.get("selected_surface"):
        lines.append(f"CANDIDATE: {manifest['selected_surface']}")
    if manifest.get("selected_opportunity"):
        lines.append(f"OPPORTUNITY: {manifest['selected_opportunity']}")
    observations = manifest.get("observations") or {}
    if observations:
        lines.extend(
            [
                f"Observed events: {observations.get('events')}",
                f"Observed cases: {observations.get('cases')}",
                f"Repeated paths: {observations.get('repeated_paths')}",
                "The workflow map is descriptive evidence, not automation approval.",
            ]
        )
    if (manifest.get("artifacts") or {}).get("work_system_map"):
        summary = manifest.get("summary") or {}
        lines.extend(
            [
                f"Reconstructed workflows: {summary.get('workflows')}",
                f"Decision candidates: {summary.get('decision_candidates')}",
                f"Named evidence gaps: {summary.get('evidence_gaps')}",
                "The work-system map is descriptive evidence, not automation approval.",
            ]
        )
    elif manifest.get("stage") == "evidence_inventoried":
        summary = manifest.get("summary") or {}
        lines.extend(
            [
                f"Evidence sources: {summary.get('sources')}",
                f"Skipped sources: {summary.get('skipped_sources')}",
                "System 2 must complete work_system_proposal.yaml; the compiler will validate every quote.",
                "No workflow, action authority, or shadow eligibility has been inferred yet.",
            ]
        )
    shadow = manifest.get("shadow") or {}
    if shadow:
        lines.extend(
            [
                f"Holdout cases: {shadow.get('holdout_cases')}",
                f"Raw accuracy: {_percent(shadow.get('raw_accuracy'))}",
                f"Confident coverage: {_percent(shadow.get('confident_coverage'))}",
                "Shadow evidence is not production approval.",
            ]
        )
    return "\n".join(lines)


def _add_case_fields(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--case-id-field", default="case_id")
    parser.add_argument("--text-field", default="message")
    parser.add_argument("--action-field", default="resolved_action")
    parser.add_argument("--outcome-field", default="outcome")
    parser.add_argument("--surface-field")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start", help="start the canonical Forge journey from raw evidence")
    start.add_argument("--project", type=Path, required=True)
    start.add_argument("--system-id", required=True)
    start.add_argument("--repo", action="append", default=[])
    start.add_argument("--url", action="append", default=[])
    start.add_argument("--source", type=Path, action="append", default=[])
    start.add_argument("--cases", type=Path)
    start.add_argument("--taxonomy", type=Path)
    start.add_argument("--scope")
    start.add_argument("--review-minutes", type=float, default=2.0)
    start.add_argument("--hourly-cost", type=float)
    start.add_argument("--monthly-volume", type=int)
    start.add_argument("--force", action="store_true")
    _add_case_fields(start)

    inspect = commands.add_parser("inspect", help="inspect the current stage and canonical next action")
    inspect.add_argument("project", type=Path)
    inspect.add_argument("--json", action="store_true")

    continue_command = commands.add_parser("continue", help="explain the next safe product step")
    continue_command.add_argument("project", type=Path)

    scan = commands.add_parser("scan", help="discover source-backed opportunities without historical cases")
    scan.add_argument("--project", type=Path, required=True)
    scan.add_argument("--source", type=Path, action="append", required=True)
    scan.add_argument("--system-id", required=True)
    scan.add_argument("--proposal", type=Path, help="optional System 2 proposal YAML with exact source citations")
    scan.add_argument("--force", action="store_true")

    reconstruct = commands.add_parser(
        "reconstruct",
        help="acquire evidence and reconstruct a work system with validated System 2 links",
    )
    reconstruct.add_argument("--project", type=Path, required=True)
    reconstruct.add_argument("--evidence-manifest", type=Path, help="existing evidence manifest (legacy/advanced)")
    reconstruct.add_argument("--system-id", help="stable identifier for a new direct acquisition")
    reconstruct.add_argument("--repo", action="append", default=[], help="GitHub HTTPS repository URL; repeatable")
    reconstruct.add_argument("--url", action="append", default=[], help="HTTPS evidence URL; repeatable")
    reconstruct.add_argument("--source", type=Path, action="append", default=[], help="local file or directory; repeatable")
    reconstruct.add_argument("--proposal", type=Path, help="finalize an acquired project with this System 2 proposal")
    reconstruct.add_argument("--max-files", type=int, default=evidence_acquisition.DEFAULT_MAX_FILES)
    reconstruct.add_argument(
        "--max-source-bytes",
        type=int,
        default=evidence_acquisition.DEFAULT_MAX_SOURCE_BYTES,
    )
    reconstruct.add_argument("--force", action="store_true")

    select = commands.add_parser("select", help="select one bounded hypothesis for observation")
    select.add_argument("project", type=Path)
    select.add_argument("--opportunity", required=True)

    observe = commands.add_parser("observe", help="validate event observations and compile recurring paths")
    observe.add_argument("project", type=Path)
    observe.add_argument("--events", type=Path, required=True)
    observe.add_argument("--minimum-events", type=int, default=3)
    observe.add_argument("--minimum-path-cases", type=int, default=2)

    discover = commands.add_parser("discover", help="create a reviewable Forge project")
    discover.add_argument("--project", type=Path, required=True)
    discover.add_argument("--cases", type=Path, required=True)
    discover.add_argument("--source", type=Path, action="append", default=[])
    discover.add_argument("--taxonomy", type=Path)
    discover.add_argument("--system-id", required=True)
    discover.add_argument("--scope")
    discover.add_argument("--review-minutes", type=float, default=2.0)
    discover.add_argument("--hourly-cost", type=float)
    discover.add_argument("--monthly-volume", type=int)
    discover.add_argument("--force", action="store_true")
    _add_case_fields(discover)

    integrate = commands.add_parser(
        "prepare-integration",
        help="compile non-executing adapter, action, controller, loop, verification, and telemetry contracts",
    )
    integrate.add_argument("project", type=Path)
    integrate.add_argument("--decision", dest="decision_id", help="bounded decision node ID; default is all candidates")
    integrate.add_argument("--force", action="store_true")

    propose_binding = commands.add_parser(
        "propose-bindings",
        help="validate typed binding candidates with exact source evidence; executes no target",
    )
    propose_binding.add_argument("project", type=Path)
    propose_binding.add_argument("--proposal", type=Path, required=True)

    verify_binding = commands.add_parser(
        "verify-bindings",
        help="validate external success and negative traces and promote bindings for shadow only",
    )
    verify_binding.add_argument("project", type=Path)
    verify_binding.add_argument("--observations", type=Path, required=True)

    prepare_shadow_controller = commands.add_parser(
        "prepare-controller",
        help="compile reviewed state and legality policy into a finite non-executing shadow controller",
    )
    prepare_shadow_controller.add_argument("project", type=Path)
    prepare_shadow_controller.add_argument("--proposal", type=Path, required=True)

    run_shadow_controller = commands.add_parser(
        "run-controller-shadow",
        help="ask TypeSafe JEV to choose only among legal actions and persist non-executing receipts",
    )
    run_shadow_controller.add_argument("project", type=Path)
    run_shadow_controller.add_argument("--observations", type=Path, required=True)
    run_shadow_controller.add_argument("--model", default=jev_shadow_transport.DEFAULT_MODEL)
    run_shadow_controller.add_argument("--endpoint")
    run_shadow_controller.add_argument("--timeout", type=float, default=30.0)
    run_shadow_controller.add_argument("--run-id")

    status = commands.add_parser("status", help="show the current product stage and next action")
    status.add_argument("project", type=Path)
    status.add_argument("--json", action="store_true")

    approve = commands.add_parser("approve-shadow", help="approve one candidate for non-executing evaluation")
    approve.add_argument("project", type=Path)
    approve.add_argument("--surface", required=True)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--notes")

    shadow = commands.add_parser("shadow", help="measure an approved candidate without executing actions")
    shadow.add_argument("project", type=Path)
    shadow.add_argument("--provider", choices=["typesafe", "laya"], default="typesafe")
    shadow.add_argument("--model")
    shadow.add_argument("--endpoint")
    shadow.add_argument("--timeout", type=float, default=30.0)
    shadow.add_argument("--label-source", default="historical")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            start_project(
                project=args.project, system_id=args.system_id, repositories=args.repo,
                urls=args.url, sources=args.source, cases=args.cases, taxonomy=args.taxonomy,
                scope=args.scope, case_id_field=args.case_id_field, text_field=args.text_field,
                action_field=args.action_field, outcome_field=args.outcome_field,
                surface_field=args.surface_field, review_minutes=args.review_minutes,
                hourly_cost=args.hourly_cost, monthly_volume=args.monthly_volume,
                force=args.force,
            )
            print(render_status(args.project))
        elif args.command == "inspect":
            if args.json:
                print(json.dumps(inspect_project(args.project), indent=2, ensure_ascii=False))
            else:
                print(render_status(args.project))
                print(render_next_action(args.project))
        elif args.command == "continue":
            print(render_next_action(args.project))
        elif args.command == "scan":
            proposals = None
            if args.proposal is not None:
                proposal_document = _yaml(args.proposal)
                proposals = proposal_document.get("opportunities")
                if not isinstance(proposals, list):
                    raise ProductStateError("proposal YAML must contain an opportunities list")
            scan_project(
                project=args.project,
                sources=args.source,
                system_id=args.system_id,
                proposals=proposals,
                force=args.force,
            )
            print(render_status(args.project))
        elif args.command == "reconstruct":
            direct_inputs = bool(args.repo or args.url or args.source)
            if args.evidence_manifest is not None:
                if direct_inputs or args.proposal is not None:
                    raise ProductStateError(
                        "--evidence-manifest cannot be combined with --repo, --url, --source, or --proposal"
                    )
                if not args.system_id:
                    raise ProductStateError("--system-id is required with --evidence-manifest")
                reconstruct_project(
                    project=args.project,
                    evidence_manifest=args.evidence_manifest,
                    system_id=args.system_id,
                    force=args.force,
                )
            elif args.proposal is not None:
                if direct_inputs:
                    raise ProductStateError("--proposal finalizes an existing acquired project and cannot add inputs")
                finalize_acquired_reconstruction(project=args.project, proposal=args.proposal)
            elif direct_inputs:
                if not args.system_id:
                    raise ProductStateError("--system-id is required for direct acquisition")
                acquire_reconstruction_project(
                    project=args.project,
                    system_id=args.system_id,
                    repositories=args.repo,
                    urls=args.url,
                    sources=args.source,
                    max_files=args.max_files,
                    max_source_bytes=args.max_source_bytes,
                    force=args.force,
                )
            else:
                raise ProductStateError(
                    "provide --evidence-manifest, direct --repo/--url/--source inputs, or --proposal"
                )
            print(render_status(args.project))
        elif args.command == "select":
            select_opportunity(args.project, opportunity_id=args.opportunity)
            print(render_status(args.project))
        elif args.command == "observe":
            observe_project(
                args.project,
                events=args.events,
                minimum_events=args.minimum_events,
                minimum_path_cases=args.minimum_path_cases,
            )
            print(render_status(args.project))
        elif args.command == "discover":
            discover_project(
                project=args.project,
                cases=args.cases,
                sources=args.source,
                taxonomy=args.taxonomy,
                system_id=args.system_id,
                scope=args.scope,
                case_id_field=args.case_id_field,
                text_field=args.text_field,
                action_field=args.action_field,
                outcome_field=args.outcome_field,
                surface_field=args.surface_field,
                review_minutes=args.review_minutes,
                hourly_cost=args.hourly_cost,
                monthly_volume=args.monthly_volume,
                force=args.force,
            )
            print(render_status(args.project))
        elif args.command == "prepare-integration":
            prepare_integration(args.project, decision_id=args.decision_id, force=args.force)
            print(render_status(args.project))
        elif args.command == "propose-bindings":
            propose_bindings(args.project, proposal=args.proposal)
            print(render_status(args.project))
        elif args.command == "verify-bindings":
            verify_bindings(args.project, observations=args.observations)
            print(render_status(args.project))
        elif args.command == "prepare-controller":
            prepare_controller(args.project, proposal=args.proposal)
            print(render_status(args.project))
        elif args.command == "run-controller-shadow":
            result = run_controller_shadow(
                args.project,
                observations=args.observations,
                model=args.model,
                endpoint=args.endpoint,
                timeout=args.timeout,
                run_id=args.run_id,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "status":
            if args.json:
                print(json.dumps(load_project(args.project), indent=2, ensure_ascii=False))
            else:
                print(render_status(args.project))
        elif args.command == "approve-shadow":
            approve_for_shadow(
                args.project,
                surface_id=args.surface,
                reviewer=args.reviewer,
                notes=args.notes,
            )
            print(render_status(args.project))
        elif args.command == "shadow":
            run_shadow(
                args.project,
                provider=args.provider,
                model=args.model,
                endpoint=args.endpoint,
                timeout=args.timeout,
                label_source=args.label_source,
            )
            print(render_status(args.project))
        else:  # pragma: no cover - argparse enforces this branch
            raise ProductStateError(f"unsupported command {args.command!r}")
    except (
        ProductStateError,
        event_observation.ObservationError,
        opportunity_scan.ScanError,
        discovery.DiscoveryError,
        discovered_eval.EvaluationError,
        evidence_acquisition.AcquisitionError,
        work_reconstruction.ReconstructionError,
        integration_package.IntegrationPackageError,
        binding_verification.BindingVerificationError,
        shadow_controller.ShadowControllerError,
        jev_shadow_transport.JevShadowError,
        RuntimeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
