# Changelog

## Unreleased

- Added the JEV-fit table (`jev_fit.md`, `jev_fit.yaml`) to `scan`,
  `discover`, and `reconstruct`. Each discovered decision gets Bounded,
  Frequent, Painful, and Measurable answers (`yes`/`no`/`unknown`) with
  evidence and the missing input for every `unknown`, plus a verdict.
  Cold-start rows never claim volume or outcomes.

- Added Product Coherence V1. `product_lifecycle.yaml` is now the executable
  source of truth for persisted stages, next-action vocabulary, legal
  transitions, required inputs, and safety boundaries. Project reads and
  product-facing transitions fail closed when implementation and contract drift.
- Added the public `forge.py start|inspect|continue|status` journey. `start`
  routes real source acquisition or resolved-case discovery without replacing
  the existing compilers; `inspect` combines evidence with canonical guidance;
  `continue` is actionable but byte-for-byte non-mutating. Low-level compiler,
  binding, controller, and shadow commands remain advanced interfaces.
- Replaced mocked coherence checks with real code, SOP/document, agentic-runtime,
  and resolved-case golden journeys. `start --cases` now rejects repository or
  URL inputs it cannot consume instead of silently dropping them.

- Added `forge.py run-controller-shadow`, an environment-only TypeSafe JEV
  connection for reviewed finite controllers. Deterministic code filters legal
  actions before the bounded Choice; one legal action skips the API call.
- Added privacy-safe receipts under `integration/shadow_runs/` with controller
  and source hashes, probabilities, confidence, model, usage, latency, stop
  reason, and an explicit zero-binding-invocation safety record. This remains
  shadow-only and grants no production authority.

- Added Shadow Controller V1 with `forge.py prepare-controller`. A reviewed,
  exact-source-cited proposal now compiles observable state predicates,
  deterministic per-action legality, an unconditional fallback, confidence
  policy, terminal states, and a finite fail-closed loop. The provider-neutral
  runtime accepts a JEV-shaped callback, exposes only legal action IDs, rejects
  illegal answers, fingerprints observations instead of persisting raw state,
  and never invokes a binding. The pinned OpenAI Agents workflow benchmark
  demonstrates terminal and low-confidence stops with zero binding invocations
  and no production authority.
- Added Binding Verification V1 with `forge.py propose-bindings` and
  `forge.py verify-bindings`. Agent-authored locators are type-checked against
  known actions and exact hashed source evidence without importing the target.
  A controlled host must provide both successful and safe-negative transition
  observations bound to the exact candidate digest. Persisted evidence contains
  fingerprints rather than raw state, credentials, or private reasoning. A
  passing binding is promoted only to `verified_for_shadow`; it remains
  `executable: false` with no production authority. The public-code-derived
  benchmark exercises a controlled adapter from the pinned OpenAI Agents
  inactive-issue workflow while proving that the Forge itself executes no
  target.
- Added `forge.py prepare-integration`, which compiles a mapped Work System into
  a hashed, reviewable, non-executing Integration Package containing observable-
  state, legal-action, binding, controller, loop, verification, and telemetry
  contracts. Reconstruction-only bindings are explicit stubs; state activation,
  a safe fallback, finite loop bounds, and runtime authority remain blocking
  requirements. The verifier detects cross-contract drift without importing or
  calling the target system.
- Added Direct Evidence Acquisition V1. `forge.py reconstruct` now accepts
  repeatable `--repo`, `--url`, and `--source` inputs, creates bounded hashed
  snapshots and a System 2 reconstruction request, then validates the generated
  proposal in the same persistent project. Users and skills no longer need to
  author an evidence manifest or proposal YAML. HTTPS, repository, symlink,
  binary, size, duplicate, quote, and authority boundaries fail closed. A
  deterministic benchmark reproduces the pinned public Pydantic AI and OpenAI
  Agents evidence hashes through the direct repository acquisition path.
- Added Work System Reconstruction V1 as an upstream product stage. A validated
  System 2 proposal can connect hashed policy documents, workflow definitions,
  templates, and public histories into actors, artifacts, states, activities,
  bounded decisions, outcomes, repeated paths, and named evidence gaps while
  preserving declared versus observed status. `forge.py reconstruct` persists a
  reviewable, descriptive project. The first public benchmark covers Pydantic AI
  and OpenAI Agents SDK with commit-pinned sources and captured issue/PR cases.
- Added Observed Runtime Benchmark V1 with pinned OpenAI Agents SDK and Vajra
  commits, licenses, passing offline baseline commands, hashed capture adapters,
  and eight events emitted by actual repository execution paths. Both event sets
  compile through the production observation core; OpenAI demonstrates one
  recurring two-step agent handoff across independent cases, while Vajra remains
  correctly below workflow-readiness. Provenance, private-reasoning, illegal
  action, insufficient-coverage, and source-integrity regressions are tested.
- Added Real-world Benchmark V1.1 negative controls and conservative recovery
  for explicit bounded choices in LLM calls and operating notes.
- Added four exact external excerpts with pinned raw URLs, upstream line spans,
  SHA-256 verification, and an optional network provenance verifier.
- Started V1.2 with exact Anthropic structured-extraction and repeated Vajra
  routing controls; readiness remains HOLD until the 10-case multi-ecosystem
  external corpus is complete.
- Completed V1.2 external coverage with an exact OpenAI Structured Outputs enum
  router cell and a paired open-generation cell using deterministic notebook
  extraction and raw-file hash verification.
- Product contract: `docs/product-target.md` fixes the final outcome as finding
  repeated decisions and routing them to deterministic code, observed JEV
  evaluation, System 2, or further evidence. A new executable acceptance corpus
  covers six input archetypes and runs through
  `scripts/evaluate_product_contract.py`; product increments now have a durable
  cross-input regression gate instead of relying on single-repository demos.
- Observation lifecycle: `forge.py select` emits a JSON event schema for one
  bounded human or agentic hypothesis; `forge.py observe` validates cumulative
  JSONL events and compiles repeated action sequences into a descriptive
  Decision System Map. Raw state, event IDs, and case IDs remain external;
  hidden reasoning, illegal actions, mismatched actors, and ambiguous event
  ordering are rejected. This stage still creates no JEV call or runtime authority.
- Cold-start discovery: `scripts/forge.py scan` inventories code and operating
  material when users have no resolved cases or named decision surface. It
  separates deterministic rules, bounded semantic decisions, and open
  generation into a hypothesis-only Decision Opportunity Map, then emits a
  normalized observation plan. It creates no executable binding, candidate
  bundle, or shadow eligibility. Optional System 2 proposals require exact
  source-line evidence and cannot invent actions absent from that evidence.
- Product V1 lifecycle: `scripts/forge.py scan|select|observe|discover|status|approve-shadow|shadow`
  turns the compiler into one persistent discovery-to-measurement project. It
  generates a domain-owner `review.md`, records an auditable shadow-only
  approval, refuses invalid stage transitions, and persists the next safe
  action and measured holdout evidence without executing discovered actions.
- `docs/product-v1.md` defines the product outcome, state machine, safety
  contract, acceptance criteria, deliberate non-goals, and the path from local
  decision surfaces to future hidden-workflow discovery. The installed skill
  now uses this product lifecycle by default and keeps low-level scripts for
  diagnostics and compiler development.
- Cross-CLI skill activation now resolves packaged scripts from the installed
  skill root, advertises `$decision-system-forge` for Codex and
  `/decision-system-forge` for Claude Code, and persists generated projects in
  the user's workspace. `install.sh --check` detects missing or stale symlinks;
  the Codex, Claude, Copilot, Gemini, and shared skill links now point at the
  active checkout.
- Rename the project and installed skill from `action-vocabulary-forge` to
  `decision-system-forge`, reflecting the complete source-to-evaluated-runtime
  product rather than only its legal-action vocabulary.
- `discover_decision_system.py`: offline product entry point for a repository/SOP set plus resolved JSONL/CSV cases. It validates and groups histories, ranks bounded decision surfaces by evidence readiness and optional workload value, creates a privacy-safe stratified holdout, reports a clearly labeled local text baseline, and scaffolds the highest-ranked eligible surface as a non-production Semantic Decision Bundle.
- Candidate discovery never copies raw case context into its outputs, never invents bindings, requires human approval for non-fallback actions, and suppresses bundle generation when evidence or boundedness gates fail. `references/decision-discovery.md` defines the input contract, scoring, outputs, and promotion path; `examples/discovery-input/` provides the tested vertical slice.
- `evaluate_discovered_system.py`: shadow-only JEV/Laya evaluation on the frozen deterministic holdout. It verifies the original source hash, rejects illegal model answers, writes only hashed case references, distinguishes historical from human-verified labels, and produces a `jev_gate.py`-compatible log plus measured performance JSON.
- Refresh the executive comic for the semantic compiler flow and add an editable SVG source.
- Semantic Decision Bundle: `material_manifest.yaml`, `semantic_ir.yaml`, `judgment_registry.yaml`, and `semantic_links.yaml` extend the compatible Action Bundle from arbitrary source material through semantic judgments to legal actions.
- `init_semantic_bundle.py` and `validate_semantic_bundle.py`: scaffold and enforce provenance, maturity, question shapes, cross-file links, and the invariant that a judgment cannot authorize an action.
- `semantic_runtime.py`: two-stage execution. It evaluates active reviewed Choice/Noul/Score judgments, enriches the final action context, filters the Choice to actions whose deterministic preconditions pass, selects a single legal action without a second model call, and refuses a missing legal fallback.
- `semantic_index.py`: generated SQLite FTS5 search across sources, concepts, relations, question families, judgments, states, actions, surfaces, and evidence.
- `JudgmentLog`: raw supporting answers in the bundle-free `jev_gate.py` format, so question instruments and final actions can be evaluated independently.
- `scripts/jev_gate.py calibrate|evaluate`: thresholds and the release gate for any JEV or Laya decision log, with no bundle and no PyYAML. Accepts plain `answer/confidence` or the raw System One answer (`choice`, `noul`, `score`), per-question abstain values, human-labels-only gate, and replays the thresholds on the held-out split to report the automation rate.
- The calibration rule, metrics and bundle-free gate checks moved into `decision_history.py` (`calibrate_groups`, `log_metrics`, `gate_failures`, `threshold_failures`); `calibrate_thresholds.py` and `evaluate_decisions.py` now call them, with unchanged output.
- Fix: calibration and the release gate treated a Noul's `no_action_id` as a free fallback even when the question declares a distinct `abstention_action_id`, so "no" was never calibrated and the gate never required a threshold for it. They now use the adapter's rule; a test pins the two implementations together.
- Escalation cascade: `decide()` / `run()` take `escalate=callable(context, decision, legal) -> action_id | None`. An abstained decision goes to the second decider (an LLM, a rule) before the fallback runs. It is offered only the question's non-fallback actions legal from the current state; `None` keeps the fallback; anything else raises `IllegalChoice`. Dynamic-candidate questions are not escalated.
- `Decision.decided_by` and the log field `decided_by`: `jev | fallback | escalation`. An escalated decision keeps `abstained: true` (JEV did abstain) and still passes every execution check; an escalated action with `requires_confirmation` is always blocked, even with `confirmed=True`.
- `label_source` on labels (JSONL/CSV column or inline in the log; missing means `human`). `evaluate_decisions.py` judges the release gate on human labels only and prints `excluded_machine_labeled`: an LLM that labels and escalates would otherwise grade itself. Calibration accepts every source and prints the counts.
- Evaluation: escalated records count as decisions in boundary accuracy, an escalation that acted where the truth was a fallback fails abstention accuracy, and a new `escalation_accuracy` line reports the second decider alone.

## 0.4.0 (2026-09-22)

- A Noul's `no_action_id` is a free fallback only when the question declares no `abstention_action_id`. With one declared, "no" is a conclusion and must clear its threshold: a control test that can record an exception ungated is not a control test.
- `calibrate_thresholds.py --min-threshold` (default 0.5): a calibrated threshold can no longer fall to the bottom floor and silently ungate an action when a small sample makes every confidence band look perfect. Clamped values are marked `*` and the floor is recorded in the policy. Found when a local model produced its only wrong conclusion on an action calibrated to 0.00.
- `criterion_compact` / `instruction_compact`: a question may carry a short wording used by providers with a small context window (`COMPACT_PROVIDERS`, currently `laya`); `FORGE_COMPACT_CRITERIA=1|0` forces it. The validator requires compact criteria on every choice or none.
- `provider: laya`: in-process local transport (Laya, Apache-2.0) with the same answer shape as TypeSafe System One, embedded into generated adapters; `FORGE_PROVIDER` env override; `default_transport()`.
- Calibration skips records without a confidence (deterministic decisions); `evaluate_decisions.py` reports deterministic agreement separately (a disagreement holds the release) and gains `--by-model`.
- The Laya transport reports the winning probability as `confidence` and keeps the provider's own value as `native_confidence`: Laya's native confidence is a margin topping out near 0.3, which collapsed every record into the lowest calibration bin so no group could ever calibrate.
- Python 3.11 compatibility: nested same-quote f-strings (PEP 701, 3.12+) removed; a test parses every script at `feature_version=(3, 11)`. Found running a generated adapter on Intel macOS, where torch caps at 2.2.2 and the venv must be 3.11.
- First measured provider comparison on one bundle (60 labeled samples, internal-control testing): hosted `jev-1.13.0` 97.3% raw agreement and 95% of decisions executed; local `laya:typed-decisions` 90.0% and 31% executed; **zero wrong conclusions after thresholds on either**, and the gate held the local one by naming the attribute that never reached the accuracy target.

## 0.3.0 (2026-09-22)

- `ui` bindings render to Playwright handlers (`goto/click/fill/select/press/check/uncheck/read` on a locator template, optional `url`), on a host-injected page (`set_ui_page`) or a headless browser per call.
- `mcp` bindings render to MCP `tools/call` handlers over stdio or streamable HTTP via the MCP Python SDK, or through a host-injected caller (`set_mcp_caller`).
- Missing SDKs raise `ExecutionBlocked` with the install command; nothing is silently skipped.
- Validator: kind-specific checks for `ui` (operation, driver, url scheme, `value` for fill/select/press) and `mcp` (transport, command/url).
- No binding kind renders as `stub:unsupported_kind` any more; stubs remain only for missing or unobserved evidence.

## 0.2.0 (2026-09-21)

- `generate_adapter.py` renders handlers from evidence-graded `binding`s (`python_callable`, `http`, `cli`); `mcp`/`ui` and unobserved bindings become stubs that name the missing evidence.
- Generated adapter re-checks `preconditions[]` and `allowed_from_states`, infers the state from `observable_predicate`, and exposes `legal_actions()`.
- Decision log (`DecisionLog`, `decision_record()`), `decide()` and `run()` entry points, `transport=` for tests.
- Policy per question and per action (`policy.questions`), `default_when_uncalibrated: abstain`.
- `criteria_source: dynamic` questions with runtime choices mapped to `dynamic_executor_action_id`.
- `model` and `endpoint` from `jev_adapter_spec.yaml` carried into the adapter.
- `scripts/predicates.py`: one grammar for preconditions, observable predicates and guards, embedded into the adapter.
- `scripts/calibrate_thresholds.py` and `scripts/evaluate_decisions.py` with the release gate; `scripts/decision_history.py` shared helpers.
- Validator: `validate()` API, binding/policy/question-type/predicate/fallback-safety checks, secret detection.
- Example bundle gains bindings and is regenerated from `init_action_bundle.py --example` (drift is a pre-commit failure).
- Repo layout: README, MIT license, `scripts/install.sh`, `.githooks/pre-commit`.

## 0.1.0 (2026-09-21)

- Discovery skill, bundle schema, initializer, scanner, validator, surface compiler, minimal JEV runner, first `generate_adapter.py`.
## Unreleased

- Added the provenance-backed Real-world Benchmark V1 with pinned GitHub
  excerpts, deterministic metrics, malformed-input rejection, and an explicit
  HOLD when current discovery misses document-only and expensive-LLM cases.
