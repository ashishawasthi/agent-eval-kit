"""agent-eval-kit: the shared evaluation scaffold for hexagonal agent repos.

One versioned source of truth for the eval layer every catalog vertical was re-implementing:

* **The report types** (:mod:`agent_eval_kit.report`) - ``EvalMetricResult`` / ``EvalReport``
  and their console rendering, the vertical-neutral shape both evaluators speak.
* **The ``--mode smoke|gate`` scaffold** (:mod:`agent_eval_kit.modes`) - ``eval_main`` gives a
  repo the standard CLI, aligned report output, and the fail-closed exit codes; the repo
  supplies only its offline scorer and its gate runner.
* **The Hrz4 gate client** (:mod:`agent_eval_kit.gate_client`) - the one HTTP contract for the
  shared promotion gate (structured target, registered bundle, ``results[]`` parse, POST gate).
* **The not-falsely-green harness** (:mod:`agent_eval_kit.harness`) - ``assert_can_go_red`` turns
  "prove this metric can fail" into a one-liner, the direct generalisation of the C4 rollout's
  most expensive lesson.

The report/modes/harness layers are pure stdlib; the gate client needs ``httpx``. Kept
independent of the other commons packages: the gate client takes injectable auth headers so a
consumer can pass ``hex_service_kit.s2s.client_headers()`` without a hard dependency.
"""

from __future__ import annotations

from . import gate_client, harness, modes, report
from .gate_client import GateClientError, Hrz4GateClient
from .harness import NotFalselyGreenError, assert_can_go_red, assert_each_can_go_red
from .modes import GateRunner, SmokeRunner, build_parser, eval_main
from .report import EvalMetricResult, EvalReport, print_report

__version__ = "0.1.0"

__all__ = [
    "EvalMetricResult",
    "EvalReport",
    "GateClientError",
    "GateRunner",
    "Hrz4GateClient",
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
