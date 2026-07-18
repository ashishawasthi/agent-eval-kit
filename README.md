# agent-eval-kit

The shared **evaluation scaffold** for hexagonal (ports-and-adapters) service repos. One versioned
source of truth for the eval layer applications re-implement: the report types, the `run_eval.py
--mode smoke|gate` CLI, a promotion-gate HTTP client, and a harness that makes "prove this metric
can go red" a one-liner.

**Pure standard library except the gate client** (which needs `httpx`).

## Why it exists

In a polyrepo, copy-paste is the only sharing mechanism, so the `--mode` split and the gate-client
contract get pasted into every service and drift. Worse, an eval metric can quietly become unable
to fail (a scorer reading its own output, a golden set that planted no target), so it is a constant
1.0 that proves nothing. This package retires both: adopt the scaffold and the harness by a version
bump.

## What you get

```python
from pathlib import Path
from agent_eval_kit import eval_main, EvalReport, EvalMetricResult, PromotionGateClient, assert_can_go_red

# 1) The --mode smoke|gate CLI. Supply your offline scorer and your gate runner; get the
#    standard CLI, aligned output, and fail-closed exit codes.
def smoke(dataset: Path) -> EvalReport:
    ...  # your deterministic heuristic evaluator
    return EvalReport(dataset=str(dataset), results=(EvalMetricResult.scored("pii_safety", 1.0, 0.99),))

def gate(dataset: Path) -> tuple[EvalReport, bool]:
    client = PromotionGateClient("https://quality.internal", bundle="example-bundle", model="my-model")
    return client.evaluate(str(dataset)), client.gate(str(dataset))

if __name__ == "__main__":
    raise SystemExit(eval_main(smoke=smoke, gate=gate, default_dataset=Path("eval/datasets/golden.jsonl")))
```

```python
# 2) Prove a metric is not structurally falsely green: it PASSES clean and FAILS degraded.
assert_can_go_red(
    my_pii_scorer,
    green="fully redacted output",
    red="applicant NRIC S1234567D leaked",   # obviously fictional
    threshold=0.99,
    metric="pii_safety",
)
```

The gate client speaks a hardened contract: a structured `target`, top-level `dataset_id` equal to
`target.dataset_id`, selection by the registered `bundle` (no bare metric names on the wire),
response parsed from `results[]`, and a POST promotion gate. Auth headers are injectable, so a
consumer passes `hex_service_kit.s2s.client_headers()` for signed S2S calls without this package
depending on `hex-service-kit`.

## Modules

| Module | What it owns | Deps |
|---|---|---|
| `report` | `EvalMetricResult`, `EvalReport`, `print_report` | stdlib |
| `modes` | `eval_main`, `build_parser` (`--mode smoke\|gate`, fail-closed exit codes) | stdlib |
| `gate_client` | `PromotionGateClient` (`evaluate` / `gate`), `GateClientError` | `httpx` |
| `harness` | `assert_can_go_red`, `assert_each_can_go_red`, `NotFalselyGreenError` | stdlib |

## Install

```sh
pip install agent-eval-kit
```

## Develop

```sh
pip install -e ".[dev]"
ruff check src tests && ruff format --check src tests && mypy src && pytest
```

The hard gate is ruff (lint) + ruff (format check, ruff pinned exactly) + mypy `--strict` (src
only) + pytest, on Python 3.12 and 3.13. `respx` mocks the gate endpoints so the contract test
never talks to a real service.

## Design invariants (do not "fix" these)

- **Fail closed in gate mode.** `eval_main` exits 0 only when BOTH the scored report passes and
  the authority's gate verdict is True, so an offline smoke result can never be relabelled a
  promotion pass.
- **The gate is a POST, not a GET.** A missing dataset is a hard error, never a silent
  `{"passed": false}` indistinguishable from a real FAIL.
- **Selection is by bundle, never bare metric names.** The service owns the metric set +
  per-bundle thresholds; the client passes them through unchanged.
- **Dependency-light.** Auth headers are injectable rather than a hard dependency on
  `hex-service-kit`, so this package installs and tests standalone.

## License

Apache-2.0.
