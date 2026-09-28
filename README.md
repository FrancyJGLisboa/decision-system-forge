# decision-system-forge

[![Decision System Forge, explained in one page](docs/img/executive-comic.jpg)](docs/executive-comic.pdf)

*One-page explainer ([PDF](docs/executive-comic.pdf), [editable SVG](docs/executive-comic.svg)).
The Forge compiles source material into evidence-backed semantic judgments, legal action
surfaces, and an evaluated runtime. Semantic judgments inform action selection but never
authorize actions; deterministic code owns legality, policy, and execution.*

Point it at source material and a decision outcome. The Forge now compiles a
**Semantic Decision Bundle**: provenance-tracked material, semantic concepts,
reusable Choice/Noul/Score judgments, observable states, legal actions,
decision surfaces, and a generated adapter that lets TypeSafe's JEV decide
inside deterministic guard rails. The original eight-file **Action Bundle**
remains supported for focused decision-point audits.

If the decision point is not known yet, point Forge at the repository or
operating material. With no historical cases, cold-start scan separates
deterministic rules, bounded semantic decisions, and open generation, then
writes a source-backed Decision Opportunity Map and an observation plan. These
are hypotheses, not runnable decisions. When resolved cases exist, the discovery
compiler ranks bounded surfaces, measures a disjoint local baseline, and
scaffolds the safest candidate. Neither path promotes observed behavior into
production authority.

```text
material
  -> discovery writes a manifest, semantic IR, judgment registry and evidence
  -> legal actions and local decision surfaces are compiled from that structure
  -> validate_semantic_bundle.py refuses unsupported or unsafe links
  -> semantic_index.py makes the vocabulary searchable
  -> semantic_runtime.py evaluates active judgments, then exposes only legal actions
  -> generate_adapter.py renders the adapter: JEV call, policy, gates, handlers, log
  -> the adapter runs; every decision lands in decision_log.jsonl
  -> calibrate_thresholds.py turns labeled history into per-action thresholds
  -> evaluate_decisions.py prints the metrics and RELEASE GATE: APPROVE | HOLD
  -> a human grants credentials, answers the gate, resolves abstentions
```

JEV answers bounded questions. Supporting judgments interpret semantic properties;
the final action Choice sees only actions already legal in the observable state.
Code decides legality, applies thresholds and abstention, re-checks preconditions,
and executes through a handler generated from an observed binding, never a guess.

## Product V1: cold start to shadow mode

The public journey is intentionally small: `start` routes supplied evidence to
the appropriate existing compiler, `inspect` explains the current stage, and
`continue` reports the next safe step. Low-level commands remain available for
audits and implementation work, but they are not the product contract.

```bash
python3 scripts/forge.py start --project ./.forge/my-system \
  --system-id my_system --source ./docs --source ./src
python3 scripts/forge.py inspect ./.forge/my-system
python3 scripts/forge.py continue ./.forge/my-system
```

The canonical lifecycle, entry paths, transitions, and safety boundaries live
in [`product_lifecycle.yaml`](product_lifecycle.yaml). The destination is a
measured, non-executing JEV shadow workflow; no semantic judgment grants action
authority.

The product entry point wraps the compiler lifecycle in one persistent Forge
project. Users and skills should prefer it over coordinating the low-level
scripts directly:

```bash
# Heterogeneous public or private evidence: no manifest authoring required.
python3 scripts/forge.py reconstruct \
  --project ./forge-project \
  --repo https://github.com/example/operations \
  --url https://example.com/operations-policy.md \
  --source ./emails-and-transcripts \
  --system-id supplier_operations

# The installed skill reads the acquired snapshots, completes the System 2
# proposal, and asks the compiler to validate it in the same invocation.
python3 scripts/forge.py reconstruct \
  --project ./forge-project \
  --proposal ./forge-project/work_system_proposal.yaml

# Turn the validated map into a fail-closed implementation contract.
python3 scripts/forge.py prepare-integration ./forge-project

# Let an implementation agent propose typed bindings, then validate evidence
# emitted by a controlled external harness. Neither command grants execution.
python3 scripts/forge.py propose-bindings ./forge-project \
  --proposal ./binding_proposal.yaml
python3 scripts/forge.py verify-bindings ./forge-project \
  --observations ./binding_observations.jsonl

# Compile reviewed state, legality, fallback, confidence, and finite-loop rules.
# The resulting controller calls a host-supplied decider but executes no action.
python3 scripts/forge.py prepare-controller ./forge-project \
  --proposal ./controller_proposal.yaml

# Connect the reviewed controller to TypeSafe JEV. The environment key is never persisted.
python3 scripts/forge.py run-controller-shadow ./forge-project \
  --observations ./observable-states.jsonl

# No history required: find candidate human, agentic, and software decisions.
python3 scripts/forge.py scan \
  --project ./forge-project \
  --source ./SOPs \
  --source ./src \
  --system-id supplier_operations

python3 scripts/forge.py select ./forge-project \
  --opportunity supplier_exception
python3 scripts/forge.py observe ./forge-project \
  --events ./decision-events.jsonl

# When resolved cases exist, build and measure an evidence-backed candidate.
python3 scripts/forge.py discover \
  --project ./forge-project \
  --source ./SOPs \
  --cases ./resolved-cases.jsonl \
  --surface-field decision_type \
  --system-id supplier_operations

python3 scripts/forge.py status ./forge-project
python3 scripts/forge.py approve-shadow ./forge-project \
  --surface supplier_exception \
  --reviewer "Domain Owner"
TYPESAFE_API_KEY=... python3 scripts/forge.py shadow ./forge-project
```

Every `scan`, `discover`, and `reconstruct` run also writes `jev_fit.md` and
`jev_fit.yaml`: one row per discovered decision answering Bounded, Frequent,
Painful, and Measurable with `yes`, `no`, or `unknown`, the evidence behind each
answer, and the missing input that would settle an `unknown`. Three `yes`
answers mark a JEV candidate. Workload and outcome answers stay `unknown` until
volumes, costs, or outcomes are supplied; the table grants no authority.

`scan` creates `scan_review.md`, `decision_opportunity_map.yaml`, and an
`observation_plan.yaml`; it creates no bundle or executable binding. `select`
creates an observation-only instrumentation contract. `observe` validates a
cumulative external JSONL log and compiles recurring action paths into a
descriptive `decision_system_map.yaml` without copying raw state or identifiers.
`discover` creates a human-readable `review.md` and durable
`forge_project.yaml` from
observed cases. `approve-shadow` records permission for non-executing evaluation
only. `shadow` is refused before that review and never executes a discovered
action. See [the V1 product specification](docs/product-v1.md).

`reconstruct` is the upstream path for mixed repositories, URLs, documents,
workflow definitions, and public operational histories. Its first phase safely
snapshots bounded text evidence, records origins and hashes, and writes a
`reconstruction_request.md` plus proposal template. The skill uses System 2 to
complete that template; the second phase compiles a source-cited
`work_system_map.yaml` containing actors, artifacts, states, activities,
decisions, outcomes, repeated workflows, and explicit gaps. The user does not
author a manifest or YAML. The compiler rejects missing quotes, unknown sources,
or attempts to promote declared material into observed behavior. Existing
prebuilt evidence manifests remain supported as an advanced interface. See
[work-system reconstruction](references/work-system-reconstruction.md).

`prepare-integration` bridges reconstruction and implementation without
pretending the target is already runnable. It writes a hashed Integration
Package covering observable state, action IDs, legal-action filtering, binding
verification, controller steps, loop stop conditions, telemetry, and contract
checks. Every reconstruction-only binding is a non-executable stub; no fallback
or state activation is guessed. See
[integration packages](references/integration-package.md).

`propose-bindings` is the next reviewed transition. It checks that each
agent-authored candidate targets a known action, uses a closed kind-specific
locator, and cites an exact quote from unchanged acquired evidence.
`verify-bindings` consumes success and safe-negative traces emitted by a
controlled host. It archives fingerprints rather than raw state and can mark a
binding `verified_for_shadow`, but leaves `executable: false`, legality
unverified, the controller loop blocked, and production authority absent. The
Forge does not import or invoke the proposed operation. See
[binding verification](references/binding-verification.md).

`prepare-controller` closes the next integration gap. It validates exact
source-cited state predicates and per-action legality, requires an unconditional
fallback, confidence threshold, terminal state, complete stop conditions, and a
finite iteration limit. The packaged runtime gives a JEV-compatible callback
only the actions that deterministic code found legal, rejects illegal answers,
and stores observation hashes rather than raw state. It never invokes a binding.
See [shadow controllers](references/shadow-controller.md).

`run-controller-shadow` is the provider connection for that reviewed plan. It
reads `TYPESAFE_API_KEY` from the process environment, deterministically filters
the legal action IDs before each request, and sends one bounded TypeSafe Choice.
Raw observations and credentials are not written to disk. Each run writes a
hashed YAML manifest and JSONL answer receipts under
`integration/shadow_runs/`, including model, probabilities, confidence, token
usage, latency, policy outcome, and zero binding invocations. It remains
shadow-only: no action is executed and no production authority is granted. The
next promotion gate is trusted labels and calibration for the exact question,
state builder, and model version.

The durable target is defined by the
[final product contract](docs/product-target.md), not by the number of language
parsers. Its executable acceptance corpus covers Python source, a TypeScript/DOT
agentic workflow, documents-only discovery, mixed operating material, an
expensive bounded LLM router, and resolved histories:

```bash
python3 scripts/evaluate_product_contract.py
python3 scripts/work_system_benchmark.py
python3 scripts/direct_acquisition_benchmark.py
python3 scripts/integration_package_benchmark.py
python3 scripts/binding_verification_benchmark.py
python3 scripts/shadow_controller_benchmark.py
```

Every real-world miss should become a pinned scenario before its fix is accepted.

The next evidence layer executes real public agent runtimes offline and compiles
their emitted decisions through the production observation core:

```bash
python3 scripts/observed_runtime_benchmark.py --list-runtimes
python3 scripts/observed_runtime_benchmark.py --verify-provenance
python3 scripts/observed_runtime_benchmark.py --verify-safety
python3 scripts/observed_runtime_benchmark.py --require-repeated-path
```

The frozen V1 corpus covers OpenAI Agents SDK handoffs and Vajra plan-review
routing. It uses deterministic test models or repository fakes, makes no paid
model calls, persists no private reasoning, and executes no discovered action.
One recurring two-handoff path is workflow-ready for the next trusted-label
shadow increment; the non-recurring Vajra paths correctly remain descriptive.

The lower-level compiler remains available for bundle development, inspection,
and debugging.

## Semantic compiler

Start from company material and resolved cases:

```bash
python3 scripts/discover_decision_system.py \
  --source examples/discovery-input/sop.md \
  --cases examples/discovery-input/cases.jsonl \
  --surface-field decision_type \
  --system-id shipment_triage \
  --review-minutes 2 --hourly-cost 45 --monthly-volume 3000 \
  --output /tmp/forge-discovery
```

This writes a source manifest, ranked candidates, privacy-safe train/holdout
references, a measured offline baseline, and a validator-clean but non-production
`candidate_bundle/`. See [decision discovery](references/decision-discovery.md).

After reviewing that vocabulary, measure the actual candidate Choice without
executing anything:

```bash
TYPESAFE_API_KEY=... python3 scripts/evaluate_discovered_system.py /tmp/forge-discovery
```

The evaluator reloads the unchanged original cases, uses only the frozen
holdout, rejects illegal answers, and writes a privacy-safe `jev_gate.py` log.

Continue with a reviewed bundle:

```bash
python3 scripts/init_semantic_bundle.py ./semantic-bundle --example
python3 scripts/validate_semantic_bundle.py ./semantic-bundle
python3 scripts/semantic_index.py build ./semantic-bundle ./semantic-bundle/semantic.sqlite
python3 scripts/semantic_runtime.py ./semantic-bundle --state-file state.json --context-file context.json
python3 scripts/generate_adapter.py ./semantic-bundle --output ./semantic-bundle/generated_adapter.py
```

The runtime is two-stage: active reviewed judgments are evaluated first; their
typed answers enrich a final Choice compiled from the currently legal actions.
One legal action is selected deterministically. No legal fallback stops the run.
`JudgmentLog` produces `jev_gate.py`-compatible records so supporting judgments,
not only final actions, can be calibrated against trusted labels.

## The mental model

Two analogies get you most of the way, and it is worth knowing what each one leaves out.

**A scoped action graph for a classifier.** A state machine where each state carries the small
set of actions legal from there, and the model is only ever asked to pick within that set. The
"scoped" part is load-bearing: a decision surface is local to one state, never a global menu.

**An action space with verifiable preconditions**, if you come from reinforcement learning — but
the policy is not learned. It is calibrated from your own labelled decisions, and abstention is a
first-class outcome rather than one action among many.

What both metaphors miss is what makes it usable: every node and edge carries its **provenance**
(where it was observed, at what evidence grade, refused by the validator if only inferred); every
action carries a **binding**, so the graph knows how to execute itself, and only when the
invocation was actually observed; and a **policy layer** sits over the graph with calibrated
thresholds, a mandatory abstention path, and a release gate a human answers.

A scoped action graph, plus provenance, plus executability, plus a gate.

## Status

The semantic compiler is new and covered by a validated example plus offline
two-stage runtime tests. The action-runtime core has one real system wired end to
end (a question-routing surface in an internal
ag-commodity tool: 5 generated handlers, JEV 53/54 vs 33/54 for the keyword
resolver it replaced, release gate approved). A second system (an internal-control test) ran 110 labelled decisions through
both a hosted and a fully local classifier: 97.3% and 93.6% raw agreement,
**zero wrong conclusions after thresholds on either**, with the local one
concluding 62 decisions where the hosted one concluded 105.

`python_callable`, `http` and `cli` handlers have run for real; `ui` (Playwright)
and `mcp` (MCP SDK) renderers are unit-tested at the SDK boundary but not yet
exercised against a live browser or server. Runs against TypeSafe JEV or a
self-hosted Laya checkpoint (`provider: laya`); the bundle, thresholds and gate do
not change. Expect the bundle schema to move; the validator is the contract.

## Install as a skill

```bash
git clone https://github.com/FrancyJGLisboa/decision-system-forge ~/projects/decision-system-forge
~/projects/decision-system-forge/scripts/install.sh      # symlinks into Claude, Codex, Copilot, Gemini
~/projects/decision-system-forge/scripts/install.sh --check
```

Start a new CLI session after installation, then invoke the skill directly:

```text
Codex:       $decision-system-forge discover repeated decisions in this workspace
Claude Code: /decision-system-forge discover repeated decisions in this workspace
```

The skill resolves its packaged scripts from its own installation directory, so
it can be invoked from any workspace; generated projects remain in the user's
workspace rather than inside the installed skill.

Requires Python 3.11+ and PyYAML. `ui` handlers need Playwright and `mcp` handlers the `mcp` package, only on the host that runs them. `TYPESAFE_API_KEY` is read from the
environment at call time and never written into a bundle.

Long-form explainer for people and agents: [docs/what-the-forge-is.md](docs/what-the-forge-is.md).

## Layout

```text
SKILL.md                     material -> judgments -> legal actions -> evaluated runtime
references/semantic-decision-schema.md   semantic manifest, IR, judgments, links and runtime plan
references/cold-start-discovery.md no-history System 2 proposal and observation contract
references/decision-discovery.md   resolved-case contract, ranking, baseline and promotion path
references/bundle-schema.md  every bundle field, including binding, policy, criteria_source, predicates
references/adapter-generation.md   what the generated module contains and how a host uses it
references/evaluation.md     metrics, calibration rule, release gate
references/source-playbook.md   mixed-source discovery guidance
scripts/init_action_bundle.py       scaffold an empty or example bundle
scripts/init_semantic_bundle.py     semantic front end plus the compatible Action Bundle
scripts/forge.py                    product CLI: cold scan, discovery, review and shadow state
scripts/evaluate_product_contract.py final target + cross-input acceptance corpus
scripts/scan_decision_opportunities.py no-history source scan -> opportunity map hypotheses
scripts/observe_decision_events.py normalized events -> privacy-safe recurring workflow map
scripts/discover_decision_system.py material + resolved cases -> ranked candidates + safe bundle
scripts/evaluate_discovered_system.py candidate Choice -> measured shadow holdout, no execution
scripts/scan_llm_opportunities.py   heuristic scan for classifier-replaceable generative calls
scripts/evaluate_llm_opportunity_scanner.py frozen exact-line precision/recall gate for the scanner
scripts/validate_action_bundle.py   structural and safety checks
scripts/validate_semantic_bundle.py semantic provenance, judgment and cross-link checks
scripts/semantic_index.py           SQLite FTS index over the compiled vocabulary
scripts/semantic_runtime.py         active judgments -> filtered legal Choice -> adapter execution
scripts/compile_jev_surface.py      one surface, one state -> compiled choice set
scripts/generate_adapter.py         bundle -> Python adapter (embeds scripts/predicates.py)
scripts/calibrate_thresholds.py     decision log + labels -> policy thresholds
scripts/evaluate_decisions.py       held-out metrics + release gate
scripts/run_jev_choice.py           minimal manual JEV call for a compiled surface
scripts/jev_shadow_transport.py     reviewed controller -> JEV -> shadow_runs receipts
scripts/jev_gate.py                 calibrate + release gate for any JEV decision log, no bundle
scripts/decision_history.py         shared core: labels, split, calibration, metrics, gate checks
examples/validation-bundle/         the reference bundle used by the tests
examples/semantic-validation-bundle/ full material-to-runtime reference bundle
examples/discovery-input/           representative SOP and resolved-case history
examples/cold-start-agent/          no-history agentic workflow scan fixture
tests/                              unit tests per feature plus test_end_to_end.py
```

## Calibration and gate without a bundle

Using JEV (or Laya) for routing, scoring or classification with no action to execute? You
still need thresholds from data and a held-out check on human labels. `jev_gate.py` does only
that: one JSONL record per decision (`case_id, question_id, answer, confidence, truth`, or the
raw JEV answer as `jev`), no bundle, no PyYAML.

```bash
python3 scripts/jev_gate.py calibrate decisions.jsonl --abstain human --out thresholds.json
python3 scripts/jev_gate.py evaluate  decisions.jsonl --abstain human --thresholds thresholds.json
```

It shares its core (`decision_history.py`) with the bundle scripts, so the calibration rule,
the 0.5 floor and the human-labels-only gate are the same code.

## Try it

```bash
cd ~/projects/decision-system-forge
python3 -m unittest discover -s tests -v
python3 scripts/validate_action_bundle.py examples/validation-bundle
python3 scripts/generate_adapter.py examples/validation-bundle --output /tmp/forge/adapter.py
python3 -c "import sys; sys.path.insert(0,'tests'); from test_end_to_end import write_fixture; write_fixture('/tmp/forge')"
python3 scripts/calibrate_thresholds.py /tmp/forge/bundle --log /tmp/forge/decision_log.jsonl --labels /tmp/forge/labels.jsonl --write
python3 scripts/evaluate_decisions.py /tmp/forge/bundle --log /tmp/forge/decision_log.jsonl --labels /tmp/forge/labels.jsonl
```

## Editing

`examples/validation-bundle/` and `examples/semantic-validation-bundle/` are
generated from their matching `init_*_bundle.py --example` scripts. Edit the
initializer and regenerate with `--force`. The pre-commit hook runs the tests,
validates both examples, and refuses drift. The references are hand-written.
# Optional JEV opportunity triage

Set `TYPESAFE_API_KEY` and opt in explicitly:

```sh
TYPESAFE_API_KEY=... python3 scripts/scan_llm_opportunities.py src/ --jev-triage --output opportunities.yml
```

Only this opt-in sends source windows to TypeSafe; windows are not persisted in the YAML output. Every triaged result remains a review-only `candidate`.

The scanner filters before any JEV request: Python candidates must be AST-confirmed
calls, other supported code files are scanned with comments and strings masked, and
documentation/data files are ignored. Raw HTTP calls qualify only when their local
source window contains a recognized model-provider signal. Existing TypeSafe/System
One transport infrastructure is not a replacement opportunity.

Run the offline discovery gate before changing scanner rules:

```sh
python3 scripts/evaluate_llm_opportunity_scanner.py
```

The frozen fixture set labels exact call-site lines as `replaceable_decision`,
`open_ended_generation`, `provider_infrastructure`, or `not_ai`. The gate requires
at least 90% precision and 80% recall; its test also refuses any known fixture error.
The set combines synthetic boundaries with pinned, reviewed public-code snippets.
It prevents known regressions but does not establish broad real-repository accuracy;
add more reviewed external cases before changing thresholds or supported call forms.
