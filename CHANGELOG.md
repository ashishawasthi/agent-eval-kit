# Changelog

All notable changes to `agent-eval-kit` are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-18

First release. The evaluation scaffold for hexagonal services, as one versioned package; the
application's own scorers stay in the application.

### Added
- **`report`** - `EvalMetricResult` / `EvalReport` (passes iff every metric passes) and
  `print_report`.
- **`modes`** - `eval_main` and `build_parser`: the `run_eval.py --mode smoke|gate` scaffold. A
  project supplies its offline `smoke` scorer and its `gate` runner; the scaffold provides the CLI,
  aligned report output, and fail-closed exit codes (gate mode exits 0 only when both the report
  and the authority's verdict pass).
- **`gate_client`** - `PromotionGateClient` (`evaluate` / `gate`) and `GateClientError`: the HTTP
  contract for a promotion-gate service (structured target, top-level `dataset_id` equal to
  `target.dataset_id`, selection by registered bundle, `results[]` parse, POST gate). Auth headers
  are injectable so the client stays independent of `hex-service-kit`.
- **`harness`** - `assert_can_go_red` / `assert_each_can_go_red` / `NotFalselyGreenError`: turns
  "prove this metric can fail" into a one-liner (per market/segment), the guard against a metric
  that cannot go red.
