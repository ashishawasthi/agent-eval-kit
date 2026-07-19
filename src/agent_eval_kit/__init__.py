"""agent-eval-kit: the shared evaluation scaffold for hexagonal agent repos.

One versioned source of truth for the evaluation layer a service re-implements:

* **The report types** (:mod:`agent_eval_kit.report`) - ``EvalMetricResult`` / ``EvalReport``
  and their console rendering, the shape both evaluators speak.
* **The ``--mode smoke|gate`` scaffold** (:mod:`agent_eval_kit.modes`) - ``eval_main`` gives a
  project the standard CLI, aligned report output, and the fail-closed exit codes; the project
  supplies only its offline scorer and its gate runner.
* **The promotion-gate client** (:mod:`agent_eval_kit.gate_client`) - one HTTP contract for a
  promotion-gate service (structured target, registered bundle, ``results[]`` parse, POST gate).
* **The not-falsely-green harness** (:mod:`agent_eval_kit.harness`) - ``assert_can_go_red`` turns
  "prove this metric can fail" into a one-liner, the guard against a metric that cannot go red.

The report/modes/harness layers are pure stdlib; the gate client needs ``httpx``. Kept
dependency-light: the gate client takes injectable auth headers so a consumer can pass
``hex_service_kit.s2s.client_headers()`` without a hard dependency.
"""

from __future__ import annotations

from . import gate_client, harness, modes, report
from .gate_client import GateClientError, PromotionGateClient
from .harness import NotFalselyGreenError, assert_can_go_red, assert_each_can_go_red
from .modes import GateRunner, SmokeRunner, build_parser, eval_main
from .report import EvalMetricResult, EvalReport, print_report

__version__ = "0.1.1"

__all__ = [
    "EvalMetricResult",
    "EvalReport",
    "GateClientError",
    "GateRunner",
    "PromotionGateClient",
    "NotFalselyGreenError",
    "SmokeRunner",
    "__version__",
    "assert_can_go_red",
    "assert_each_can_go_red",
    "build_parser",
    "eval_main",
    "gate_client",
    "harness",
    "modes",
    "print_report",
    "report",
]
