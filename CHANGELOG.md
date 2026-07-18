# Changelog

All notable changes to `agent-eval-kit` are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-18

First release. Extracts the evaluation scaffold that every hexagonal agent repo in the catalog
was re-implementing (workstream 19, package 3). Working code moved from its proven sources, not
redesigned; the CDD-specific scorers stay in their repo.

### Added
- **`report`** - `EvalMetricResult` / `EvalReport` (passes iff every metric passes) and
  `print_report`. Lifted from `doc-cdd-sow-agent`'s kernel + `eval/run_eval.py`.
- **`modes`** - `eval_main` and `build_parser`: the `run_eval.py --mode smoke|gate` scaffold. A
  repo supplies its offline `smoke` scorer and its `gate` runner; the scaffold provides the CLI,
  aligned report output, and fail-closed exit codes (gate mode exits 0 only when both the report
  and the authority's verdict pass). Lifted from Doc1 WP3.
- **`gate_client`** - `Hrz4GateClient` (`evaluate` / `gate`) and `GateClientError`: the shared
  HTTP contract for the Hrz4 promotion gate (structured target, top-level `dataset_id` equal to
  `target.dataset_id`, selection by registered bundle, `results[]` parse, POST gate). Lifted from
  `doc-cdd-sow-agent`'s `adapters/platform/remote_evaluation.py`. Auth headers are injectable so
  the client stays independent of `hex-service-kit`.
- **`harness`** - `assert_can_go_red` / `assert_each_can_go_red` / `NotFalselyGreenError`: turns
  "prove this metric can fail" into a one-liner (per market/segment), the direct generalisation
  of the C4 rollout's most expensive lesson.
