# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`agent-eval-kit` is the **evaluation scaffold** for hexagonal (ports-and-adapters) services,
packaged once: the report types, the `run_eval.py --mode smoke|gate` CLI, a promotion-gate client,
and a not-falsely-green harness. An application supplies its own scorers; this package supplies the
structure around them.

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
- **Dependency-light.** The gate client takes injectable `auth_headers` rather than importing
  `hex-service-kit`, so this package installs and tests standalone. Do not add a hard dependency on
  another package to the stdlib modules.
- All example identifiers in code and tests must be obviously fictional.
- No em-dashes in `.md` files or commit messages.

## Architecture

Four modules in `src/agent_eval_kit/`, re-exported flat from `__init__.py`:

- **report.py** - `EvalMetricResult` / `EvalReport` + `print_report`.
- **modes.py** - `eval_main(smoke=..., gate=..., default_dataset=...)`. A project passes two
  callables; its own scorers stay in the application.
- **gate_client.py** - `PromotionGateClient`, an HTTP client for a promotion-gate service, with the
  base-URL https guard inlined and injectable `auth_headers`.
- **harness.py** - `assert_can_go_red` / `assert_each_can_go_red`, the guard against a metric that
  cannot go red.

The gate client speaks a specific wire contract (structured `target`, top-level `dataset_id`,
selection by `bundle`, `results[]` parse, POST `/v1/gate`); the respx test in
`tests/test_gate_client.py` pins that shape, so change the two together if the server contract
changes.
