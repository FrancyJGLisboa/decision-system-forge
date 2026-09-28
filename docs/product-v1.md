# Decision System Forge V1 product specification

## Product thesis

Decision System Forge turns repeated decisions hidden in operational work into
reviewable, evaluated decision systems. A user may begin with only operating
material, or add resolved cases when they exist. The Forge first identifies
source-backed hypotheses across human, agentic, and software behavior. With
observed histories, it can rank bounded decision surfaces, record a domain
review, and measure a candidate in shadow mode.

The product is the lifecycle, not the YAML bundle or the individual compiler
scripts. Bundles remain the auditable intermediate representation.

## V1 user outcome

A domain owner can point the Forge at source material and, without editing
bundle files or learning the internal toolchain:

1. reconstruct actors, artifacts, states, activities, decisions, outcomes, and
   missing evidence across heterogeneous material;
2. receive a Decision Opportunity Map even when no case history exists;
3. distinguish code rules, bounded semantic choices, and open generation;
4. receive an event contract for observing the most promising hypotheses;
5. validate human or agentic observations and see recurring action paths;
6. when cases exist, understand ranked candidates, evidence strength, and gaps;
7. approve one candidate for non-executing shadow evaluation;
8. measure the bounded JEV decision on a frozen holdout;
9. see the next safe step and why production release is or is not allowed.

The V1 stops before production execution. This is intentional. It establishes a
complete discovery-to-measurement product loop while preserving the existing
authority boundary.

## Primary interaction

The public interaction is `start → inspect → continue`. `start` routes raw
evidence or resolved cases to the existing proven compiler. `inspect` combines
the persisted project with `product_lifecycle.yaml`; `continue` prints the exact
safe handoff and required input without mutating the project. Compilation,
binding, controller, and shadow commands remain advanced interfaces used by the
skill after their evidence gates are satisfied.

The skill is the intended interface. It selects one of two product entry points.
For heterogeneous evidence that describes a larger work system, it passes the
user's repositories, HTTPS URLs, files, and directories directly to the Forge:

```bash
python3 scripts/forge.py reconstruct \
  --project ./forge-project \
  --repo https://github.com/example/operations \
  --url https://example.com/policy.md \
  --source ./documents \
  --system-id supplier_operations
```

This deterministic acquisition phase produces hashed snapshots, a source
catalog, a reconstruction request, and a proposal template. The skill reads
those artifacts as System 2, completes the proposal with exact citations, and
asks the compiler to validate it:

```bash
python3 scripts/forge.py reconstruct \
  --project ./forge-project \
  --proposal ./forge-project/work_system_proposal.yaml
```

The user writes no Forge YAML. The result is a descriptive Work System Map and
named gaps before any local decision surface is selected. The proposal cannot
promote declared behavior to observed behavior and cannot grant runtime authority.

To turn that map into work an implementation agent can safely consume:

```bash
python3 scripts/forge.py prepare-integration ./forge-project
```

This produces contracts for observation, legal actions, bindings, controller,
loop, verification, and telemetry. It does not create executable bindings or
an autonomous runtime. Missing state mappings, safe fallback, finite loop bound,
and verified target operations remain explicit blocking gates.

For a cold start with no resolved cases:

```bash
python3 scripts/forge.py scan \
  --project ./forge-project \
  --source ./SOPs \
  --source ./src \
  --system-id supplier_operations
```

This creates hypotheses and an observation plan only. To observe one bounded
hypothesis:

```bash
python3 scripts/forge.py select ./forge-project \
  --opportunity supplier_exception
python3 scripts/forge.py observe ./forge-project \
  --events ./decision-events.jsonl
```

`select` emits a JSON Schema; the application or human workflow writes matching
events outside the Forge project. `observe` validates a cumulative snapshot and
persists only aggregate paths plus the external source hash. If resolved cases
are already available instead:

```bash
python3 scripts/forge.py discover \
  --project ./forge-project \
  --source ./SOPs \
  --source ./src \
  --cases ./resolved-cases.jsonl \
  --surface-field decision_type \
  --system-id supplier_operations
```

The skill reads `review.md`, explains the candidate in the user's language, and
records explicit review only after the domain owner confirms it:

```bash
python3 scripts/forge.py approve-shadow ./forge-project \
  --surface supplier_exception \
  --reviewer "Domain Owner"
```

The candidate can then be measured without action execution:

```bash
TYPESAFE_API_KEY=... python3 scripts/forge.py shadow ./forge-project
python3 scripts/forge.py status ./forge-project
```

## Inputs

Cold-start scan requires:

- one or more source paths containing code or operating material;
- a system identifier.

Work-system reconstruction accepts any combination of repeatable GitHub HTTPS
repositories, HTTPS text URLs, and local files or directories. Acquisition is
bounded by file-count and per-file byte limits, skips unsupported or binary
material explicitly, snapshots accepted text, and preserves its SHA-256 and
origin. Repository evidence is pinned to the acquired commit.

The structural scanner recognizes bounded Python choice calls, deterministic
thresholds, open generation, explicit TypeScript/TSX choice vocabularies, and
labelled DOT transitions. System 2 may add proposals for other inventoried
material, but every proposal must cite exact source lines and every candidate
action must occur in that evidence.

Historical discovery additionally requires:

- resolved cases in JSONL, NDJSON, or CSV;
- a unique case identifier;
- the context available at decision time;
- the historically selected action.

Recommended:

- operating material such as SOPs, code, API definitions, and policy documents;
- a surface field when the case history contains multiple decision families;
- later outcomes;
- representative volume and review-time estimates;
- an authoritative label taxonomy.

Historical actions are observations. They are never treated as proof that the
action was correct, legal, authorized, or still executable.

## Product project

Each run creates a persistent project. Cold start produces:

```text
forge-project/
├── forge_project.yaml
├── scan_review.md
├── jev_fit.md / jev_fit.yaml        four-question JEV fit per decision
├── decision_opportunity_map.yaml
├── observation_plan.yaml
├── instrumentation_spec.yaml      after selection
├── event_schema.json              after selection
├── decision_system_map.yaml       after observation
└── evidence/
    ├── source_inventory.yaml
    └── observation_manifest.yaml  hash and aggregate counts, no raw events
```

It does not create a candidate bundle. Historical discovery produces:

```text
forge-project/
├── forge_project.yaml              product state and next action
├── review.md                       domain-owner review surface
├── jev_fit.md / jev_fit.yaml       four-question JEV fit per surface
├── shadow_review.yaml              explicit non-production approval
└── discovery/
    ├── discovery_manifest.yaml
    ├── decision_candidates.yaml
    ├── evaluation_cases.jsonl
    ├── candidate_bundle/
    ├── jev_holdout_log.jsonl       after shadow evaluation
    └── jev_performance.json        after shadow evaluation
```

Raw case text and raw case identifiers are not copied into product artifacts.
The original case source remains necessary for the frozen shadow evaluation and
is rejected if its hash changes after discovery.

Direct work-system reconstruction produces:

```text
forge-project/
├── forge_project.yaml
├── evidence_manifest.yaml
├── reconstruction_request.md
├── work_system_proposal.yaml
├── work_system_map.yaml             after compiler validation
├── work_system_review.md            after compiler validation
├── jev_fit.md / jev_fit.yaml        after compiler validation
└── evidence/
    ├── source_catalog.yaml
    └── sources/                     bounded exact snapshots
```

Unlike cold scan and case discovery, direct reconstruction intentionally stores
the accepted text snapshots so System 2 and the compiler operate on the same
immutable evidence. The project records this privacy-relevant fact explicitly.

After `prepare-integration`, the same project additionally contains:

```text
integration/
├── integration_manifest.yaml
├── action_registry.yaml
├── observable_state_adapter.yaml
├── legal_action_policy.yaml
├── controller_plan.yaml
├── loop_plan.yaml
├── verification_contract.yaml
└── telemetry_contract.yaml
```

Every artifact is hashed by the integration manifest. At this stage all target
bindings remain stubs, activation mappings are unverified, the fallback is
absent, and the loop is blocked.

When integration implementation is explicitly authorized, Binding Verification
adds `binding_candidates.yaml`, `binding_observation_schema.json`, and a hashed
`binding_manifest.yaml`. A controlled host may then emit fingerprint-only
success and safe-negative traces. Passing evidence adds
`binding_verification.yaml` plus an archived observation log and promotes the
candidate only to `verified_for_shadow`; the binding remains non-executable and
the loop remains blocked.

## State machine

```text
scan ────────────┬─ no_opportunities ──> add_operational_material
                 └─ hypotheses_ready
                           │ select one bounded hypothesis
                           ▼
                  instrumentation_ready
                           │ validate cumulative event snapshot
                           ▼
                  observations_collected ──> collect_more_observations
                           │ repeated path observed
                           ▼
                   workflow_map_ready ─────> review_decision_system_map

reconstruct --repo/--url/--source ──> evidence_inventoried
                                               │ System 2 cited proposal
                                               ▼
reconstruct --proposal ─────────────> work_system_mapped
                                               │
                                   prepare-integration
                                               ▼
                                      integration_planned
                                               │
                                      propose-bindings
                                               ▼
                                  binding_candidates_ready
                                               │ controlled host executes tests
                                      verify-bindings
                                               ▼
                             bindings_verified_for_shadow
                                               │
                                      prepare-controller
                                               ▼
                                  shadow_controller_ready
                                               │
                             run_shadow_and_collect_trusted_labels

                 ┌─ insufficient_evidence
discover ────────┤
                 └─ awaiting_review
                           │ named domain-owner review
                           ▼
                   ready_for_shadow
                           │ bounded, non-executing evaluation
                           ▼
                    shadow_measured
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
verify_labels_and_calibrate   calibrate_and_run_release_gate
```

Invalid transitions fail closed. In particular:

- cold-start opportunities remain hypotheses with zero observed cases;
- scan never produces executable bindings or a shadow-eligible bundle;
- only bounded semantic hypotheses can enter observation;
- observation rejects illegal actions, mismatched actors, ambiguous ordering,
  and private reasoning fields;
- raw state, event IDs, and case IDs remain in the external hashed event source;
- an observed recurring path is descriptive evidence, not shadow approval;
- insufficient evidence does not produce a runnable candidate;
- shadow evaluation requires a named reviewer;
- the review grants shadow permission only;
- shadow evidence is not production approval;
- V1 never executes a discovered action.

## Opportunity discovery and candidate selection

The cold-start scanner inventories sources by hash and extracts only structural
signals it can cite. It classifies opportunities as:

- `deterministic_rule`: code should continue to decide;
- `bounded_semantic_decision`: observe first, then consider JEV;
- `open_generation`: keep an LLM unless a later bounded decision can be isolated.

The observation plan defines a normalized event contract with case,
opportunity, time, actor, state before, available actions, selected action,
state after, and source reference. It explicitly excludes chain-of-thought.
After one bounded hypothesis is selected, the Forge emits a JSON Schema and can
aggregate ordered per-case actions into recurring paths and transitions. This is
the bridge from an unfamiliar setting to evidence suitable for workflow
reconstruction. The current map contains one selected opportunity; linked
multi-opportunity maps remain a later increment.

The existing discovery compiler remains the analytical core. It:

- groups resolved cases into candidate surfaces;
- checks bounded action count, sample support, context coverage, and outcomes;
- creates a disjoint stratified holdout;
- measures a small local text baseline as a repeatability signal;
- ranks candidates by evidence readiness and optional workload value;
- compiles only the highest-ranked eligible surface;
- validates the generated non-production Semantic Decision Bundle.

The local baseline is not JEV performance and is not a release gate.

## Safety and authority contract

The V1 preserves six separate questions:

1. What source-backed decision hypotheses exist?
2. What historical behavior was observed?
3. Which bounded decision is a useful candidate?
4. Has a domain owner approved its vocabulary for shadow evaluation?
5. How does JEV perform on a frozen holdout?
6. Is there sufficient authoritative evidence for production?

V1 answers the first five. It deliberately does not claim the sixth.

No discovered action receives an executable binding. No semantic judgment
authorizes an action. Policy, legal preconditions, credentials, side effects,
and production release remain outside the V1 approval.

## Acceptance criteria

The V1 vertical slice is complete when all of the following are demonstrated:

- one command creates a product project from representative material and cases;
- one command creates a hypothesis-only project when cases do not exist;
- one command acquires mixed direct inputs without user-authored YAML;
- the skill completes System 2 reconstruction and compiler validation in the
  same invocation;
- acquired repository evidence is commit-pinned and every accepted source is hashed;
- cold scan separates deterministic rules, bounded judgments, and generation;
- cold scan emits a normalized observation contract and no runnable bundle;
- selection emits an instrument contract without modifying source code;
- normalized human or agent events are validated against the selected vocabulary;
- repeated action paths compile without persisting raw state or identifiers;
- the project records a durable stage and one unambiguous next action;
- the review explains the top candidate without leaking raw case content or IDs;
- weak evidence becomes `insufficient_evidence`, not a partial runnable system;
- a wrong or unnamed reviewer cannot advance the project;
- shadow evaluation is impossible before explicit approval;
- shadow evaluation calls only the compiled bounded Choice;
- illegal model answers are rejected;
- shadow mode executes no actions;
- binding proposal validation executes no target;
- binding promotion requires both successful and safe-negative controlled-host
  evidence tied to the exact candidate digest;
- verified shadow bindings remain non-executable and carry no production authority;
- the shadow controller filters actions deterministically before JEV, rejects
  illegal answers, runs a finite loop, and never invokes a binding;
- project status persists measured accuracy, coverage, label provenance, and gate eligibility;
- the full repository test suite remains green on Python 3.11-compatible syntax.

## Deliberate V1 non-goals

- automatic production deployment;
- inferred executable bindings;
- automatic policy or legal authority;
- replacement of domain review;
- full process mining from arbitrary event streams;
- claiming that a reconstructed workflow is recurrent before events or resolved
  histories support recurrence;
- a graphical application;
- live connectors to every operational system.

## Direction after V1

The durable product contract and executable cross-input acceptance corpus live in
[`product-target.md`](product-target.md). Run
`python3 scripts/evaluate_product_contract.py` before accepting an increment as
product progress.

The final product target remains hidden-workflow discovery. Direct evidence
acquisition, source-cited System 2 reconstruction, cold-start selection, the
normalized event contract, and single-opportunity recurring-path compilation
now exist. The public acquisition benchmark proves the Forge can begin from
pinned heterogeneous repository evidence without user-authored YAML. The first
real-runtime benchmark executes pinned OpenAI Agents SDK and Vajra paths offline,
captures eight agent decisions, and proves that the Forge distinguishes a
repeated two-step path from an insufficiently repeated sample. Users still do
not need to know the decision surface or possess historical labels to begin.

The fixed next increment is trusted-label shadow preparation for the repeated
OpenAI handoff surface:

1. transform observable pre-decision state into privacy-safe evaluation cases;
2. attach independently reviewed labels rather than treating runtime choices as
   ground truth;
3. freeze train/holdout membership and source hashes;
4. evaluate JEV in shadow without performing a handoff;
5. report coverage, per-action accuracy, abstention behavior, and calibration;
6. keep the release gate on HOLD until the label and sample thresholds pass.

After that vertical slice is measured, the Forge can extend observation to
multiple opportunity IDs in one system, link semantic branch points into a
larger Decision System Map, verify real action bindings, and eventually release
reversible actions with outcome monitoring.

The V1 project schema and state machine are designed to survive that expansion:
the selected local surface becomes the first node in a larger decision-system
map rather than a throwaway prototype.
