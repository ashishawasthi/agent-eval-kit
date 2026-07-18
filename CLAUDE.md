# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`agent-eval-kit` is package 3 of the catalog commons extraction (workstream 19). It holds the
**evaluation scaffold** every hexagonal agent repo re-implemented: the report types, the
`run_eval.py --mode smoke|gate` CLI, the Hrz4 promotion-gate client, and a not-falsely-green
harness. See `genai-grc-catalog/catalog/plans/plan-commons-extraction.md`.

Sibling of `pii-pack` (package 1) and `hex-service-kit` (package 2). Catalog-coupled (it encodes
the Hrz4 gate contract), so its public-vs-private distribution is a separate decision.

## Commands

A venv exists at `.venv`. Setup from scratch:

```sh
pip install -e ".[dev]"        # httpx + ruff (pinned) + mypy + pytest + respx
```

The full CI gate, in order (all four must pass):

```sh
ruff check src tests
ruff format --check src tests   # ruff pinned EXACTLY in pyproject.toml so formatting never drifts
mypy src                        # strict; src only
pytest                          # -q, testpaths=tests
```

Run a single test:

```sh
pytest tests/test_gate_client.py -q
pytest tests/test_harness.py -k falsely_green -q
```

## Hard constraints

- **Only the gate client has a runtime dependency (`httpx`).** `report`, `modes`, `harness` are
  pure stdlib. Do not add a dependency to the stdlib modules.
- **Python >=3.12**, mypy `strict = true`, ruff line-length 100 with `E,F,I,UP,B,SIM`.
- **Fail closed.** `eval_main` gate mode exits 0 only when the scored report AND the authority's
  verdict both pass. The gate call is a POST (a missing dataset must be a hard error, never a
  silent `{"passed": false}`).
- **Independent of the other commons packages.** The gate client takes injectable `auth_headers`
  rather than importing `hex-service-kit`, so eval-kit installs and tests standalone. Do not add a
  hard dependency on a sibling commons package.
- All example identifiers in code and tests must be obviously fictional.
- No em-dashes in `.md` files or commit messages (workspace docs-style rule).

## Architecture

Four modules in `src/agent_eval_kit/`, re-exported flat from `__init__.py`:

- **report.py** - `EvalMetricResult` / `EvalReport` + `print_report`. From Doc1's `kernel.py` and
  `eval/run_eval.py`.
- **modes.py** - `eval_main(smoke=..., gate=..., default_dataset=...)`. A repo passes two
  callables; the CDD-specific scorers stayed in Doc1. From Doc1 WP3.
- **gate_client.py** - `Hrz4GateClient`. From Doc1's `remote_evaluation.py`, with the base-URL
  https guard inlined and `_s2s.headers()` replaced by an injectable `auth_headers`.
- **harness.py** - `assert_can_go_red` / `assert_each_can_go_red`, the generalisation of the C4
  not-falsely-green lesson.

The Hrz4 contract mirror lives in `hrz-ai-quality-model-risk` (the server side). If that contract
changes, `gate_client.py` and `hrz-ai-quality-model-risk` must change together; the respx test in
`tests/test_gate_client.py` pins the wire shape.
