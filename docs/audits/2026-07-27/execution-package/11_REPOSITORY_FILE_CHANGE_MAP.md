# Repository File Change Map

## 1. Proposed target tree

```text
grimoire/
  AGENTS.md
  README.md
  VERSION
  CHANGELOG.md
  REPOSITORY_INDEX.json

  src/grimoire/
    __init__.py
    cli.py
    errors.py
    status.py
    models/
    validation/
    registry/
    predicates/
    applicability/
    conflicts/
    compiler/
    verifier/
    evidence/
    sources/
    zeref/
    benchmarks/
    filesystem/

  schemas/
    project/
    standards/
    sources/
    controls/
    evidence/
    receipts/
    benchmarks/
    zeref/

  registry/
    standards/
    sources/
    profiles/
    overlays/
    crosswalks/

  standards/
    universal/
    product/
    design/
    accessibility/
    architecture/
    frontend/
    api/
    backend/
    data/
    security/
    privacy/
    legal/
    ai/
    cloud/
    cost/
    git/
    operations/

  benchmarks/
    suites/
    scenarios/
    fuzz/
    performance/
    security/
    results/

  fixtures/
    valid/
    invalid/
    hostile/
    compatibility/

  scripts/
    grimoire.py
    standards.py

  tests/
    unit/
    schema/
    property/
    fuzz/
    integration/
    security/
    performance/
    compatibility/
    end_to_end/

  docs/
    architecture/
    audits/
    operations/
    migrations/
    releases/
    sources/

  .github/
    workflows/
```

## 2. Current files to retain

- `AGENTS.md`
- `README.md`
- `REPOSITORY_INDEX.json`
- `policies/`
- `profiles/`
- `adapters/`
- `instructions/`
- `templates/`
- `sources/`
- `checks/`
- `scripts/`
- `tests/`
- `benchmarks/`
- `docs/`

Retain history and migrate incrementally.

## 3. Current files requiring correction

### `README.md`

- remove stale statement that repository will later be renamed Standards Orchestrator;
- explain Grimoire as name and Standards Orchestrator as capability;
- correct version descriptions;
- document truth model.

### `Makefile`

- rename visible commands to Grimoire;
- route canonical targets through `scripts/grimoire.py`;
- retain compatibility aliases where documented.

### `templates/project/project.json`

- update standards version pin;
- add schema-complete example;
- include industry, locations, age, data purposes, AI capabilities, and approvals.

### `scripts/project_orchestrator.py`

Replace or split into:

- validator;
- normalizer;
- resolver;
- compiler;
- verifier;
- status engine.

### `scripts/grimoire.py`

Move canonical implementation into importable package and keep this as a thin entrypoint.

### `scripts/standards.py`

Deprecation wrapper only.

### `checks/standards_orchestrator_check.py`

Expand from presence checks to:

- schema;
- normative self-compliance;
- source provenance;
- duplicate IDs;
- crosswalk validity;
- compiler smoke;
- verifier smoke.

### `policies/schemas/ai-operations.schema.json`

Correct explicit properties and add validation fixtures.

## 4. New architecture decisions

Proposed:

```text
docs/architecture/
  0009-multidimensional-status-model.md
  0010-runtime-schema-validation.md
  0011-declarative-applicability-language.md
  0012-safe-atomic-pack-compilation.md
  0013-normative-standard-registry.md
  0014-source-freshness-and-supersession.md
  0015-zeref-receipt-trust-model.md
  0016-benchmark-governance.md
  0017-runtime-and-ci-dependency-boundary.md
  0018-pack-signing-and-provenance.md
```

## 5. New schemas

- project manifest v2;
- standard record v1;
- source record v1;
- control record v1;
- evidence record v1;
- exception record v1;
- conflict record v1;
- pack receipt v2;
- Zeref profile v2;
- Zeref receipt v1;
- benchmark result v1.

## 6. Migration rule

No current Markdown standard is deleted during normalization.

Steps:

1. classify;
2. create machine record;
3. link human document;
4. add source provenance;
5. add tests;
6. mark normative;
7. only then allow automatic compilation.
