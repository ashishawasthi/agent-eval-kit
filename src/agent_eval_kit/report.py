"""The shared evaluation report types and their console rendering.

``EvalMetricResult`` / ``EvalReport`` are the vertical-neutral value objects every repo's
eval produces: a per-metric score against a threshold, and the report that passes iff every
metric meets its bar. They are pure stdlib and frozen, so the offline smoke evaluator and the
remote Hrz4 gate client both speak the same shape.

Lifted from the kernel of ``doc-cdd-sow-agent`` (``domain/kernel.py`` ``EvalMetricResult`` /
``EvalReport``), with ``print_report`` moved here from that repo's ``eval/run_eval.py`` so the
rendering is shared too.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvalMetricResult:
    """One metric's score against its threshold."""

    metric: str
    score: float
    threshold: float
    passed: bool

    @classmethod
    def scored(cls, metric: str, score: float, threshold: float) -> EvalMetricResult:
        """Build a result, deriving ``passed`` from ``score >= threshold``."""
        return cls(metric=metric, score=score, threshold=threshold, passed=score >= threshold)


@dataclass(frozen=True, slots=True)
class EvalReport:
    """A full evaluation report over a dataset; passes iff every metric passes."""

    dataset: str
    results: tuple[EvalMetricResult, ...]
    n_examples: int = 0

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)


def print_report(report: EvalReport, evaluator: str) -> None:
    """Render an :class:`EvalReport` as an aligned console table with a GATE verdict."""
    name_w = max((len(r.metric) for r in report.results), default=10)
    print(f"Evaluation report  ({evaluator})")
    print(f"  dataset : {report.dataset}")
    print(f"  examples: {report.n_examples}\n")
    header = f"  {'metric'.ljust(name_w)}   score    threshold   result"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in report.results:
        verdict = "PASS" if r.passed else "FAIL"
        print(f"  {r.metric.ljust(name_w)}   {r.score:6.3f}   {r.threshold:7.2f}     {verdict}")
    print()
    print(f"  GATE: {'PASS' if report.passed else 'FAIL'}")
