"""Data shapes for the deterministic harness.

A :class:`Scenario` is a fully reproducible description of one graph run: the
question, the *scripted* behaviour of every injected dependency, and the
expectations to assert. Every ``expect_*`` field is optional — ``None`` means
"this scenario does not assert that dimension", so a metric simply skips it.

These are plain frozen dataclasses (not YAML) so scenarios reference the real
domain types — :class:`Intent`, :class:`IntentClassification`,
:class:`BookDomain` — and stay type-checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from app.application.service_ports.llm_service import IntentClassification, RankedPick
from app.domain.entities.book import BookDomain

if TYPE_CHECKING:  # avoid importing the fakes at module import time
    from tests.harness.fakes import ScriptedDeps


@dataclass(frozen=True)
class SqlStep:
    """One scripted ``execute_select`` outcome.

    Walked in order, one step consumed per ``sql_search`` call. ``error`` set
    means the repo raises ``ValueError(error)`` (matching how ``sql_search``
    catches ``Exception`` and routes to ``repair_sql``); otherwise it returns
    ``rows``. A pair ``(SqlStep(error=...), SqlStep(rows=...))`` reads literally
    as "fail, then succeed after repair".
    """

    rows: tuple[BookDomain, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class Scenario:
    """A reproducible graph-run scenario: scripted inputs + expectations."""

    id: str
    question: str

    # --- scripted dependency behaviour ---
    classify: IntentClassification
    repairs: tuple[str, ...] = ()
    sql_steps: tuple[SqlStep, ...] = ()
    semantic_books: tuple[BookDomain, ...] = ()
    # explicit reranker output; None -> top-`limit` passthrough of candidates
    ranked: tuple[RankedPick, ...] | None = None

    # --- expectations (None = do not assert) ---
    expect_intent: str | None = None
    expect_route: tuple[str, ...] | None = None
    expect_pick_isbns: tuple[str, ...] | None = None
    expect_recall_isbns: frozenset[str] | None = None
    expect_generated_sql: bool | None = None
    expect_sql_attempts: int | None = None


@dataclass(frozen=True)
class RunResult:
    """The observable result of driving the graph once."""

    output: dict[str, Any]
    route: tuple[str, ...]
    latency_ms: float
    deps: "ScriptedDeps"

    @property
    def pick_isbns(self) -> list[str]:
        return [p["book"]["isbn13"] for p in (self.output.get("picks") or [])]


@dataclass(frozen=True)
class MetricResult:
    """One metric's verdict for one scenario.

    ``score`` is a 0.0-1.0 quality number; ``passed`` is the gate decision. Both
    are ``None`` when the scenario does not assert this metric (it is skipped,
    not failed). ``latency_ms`` reports a value but never gates (``passed=None``).
    """

    name: str
    score: float | None
    passed: bool | None
    detail: str = ""


@dataclass(frozen=True)
class ScenarioReport:
    scenario_id: str
    metrics: list[MetricResult]
    latency_ms: float

    @property
    def passed(self) -> bool:
        """A scenario passes when every *asserted* metric passes."""
        return all(m.passed for m in self.metrics if m.passed is not None)


@dataclass
class Scorecard:
    """Dataset-level aggregate over scenario reports."""

    reports: list[ScenarioReport] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.reports)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.reports if r.passed)

    @property
    def pass_rate(self) -> float:
        return self.passed_count / self.total if self.total else 0.0

    def per_metric_accuracy(self) -> dict[str, tuple[float, int]]:
        """Mean score and count of asserting scenarios, per metric name."""
        acc: dict[str, list[float]] = {}
        for report in self.reports:
            for m in report.metrics:
                if m.score is not None:
                    acc.setdefault(m.name, []).append(m.score)
        return {name: (sum(v) / len(v), len(v)) for name, v in acc.items()}

    def latency_percentiles(self) -> tuple[float, float]:
        """(p50, p95) over scenario latencies, in milliseconds."""
        lat = sorted(r.latency_ms for r in self.reports)
        if not lat:
            return (0.0, 0.0)

        def pct(p: float) -> float:
            idx = min(len(lat) - 1, int(round(p * (len(lat) - 1))))
            return lat[idx]

        return (pct(0.50), pct(0.95))

    def to_dict(self) -> dict[str, Any]:
        p50, p95 = self.latency_percentiles()
        return {
            "summary": {
                "total": self.total,
                "passed": self.passed_count,
                "pass_rate": round(self.pass_rate, 4),
                "latency_p50_ms": round(p50, 2),
                "latency_p95_ms": round(p95, 2),
            },
            "per_metric": {
                name: {"mean_score": round(mean, 4), "n": n}
                for name, (mean, n) in self.per_metric_accuracy().items()
            },
            "scenarios": [
                {
                    "id": r.scenario_id,
                    "passed": r.passed,
                    "latency_ms": round(r.latency_ms, 2),
                    "metrics": [
                        {
                            "name": m.name,
                            "score": m.score,
                            "passed": m.passed,
                            "detail": m.detail,
                        }
                        for m in r.metrics
                    ],
                }
                for r in self.reports
            ],
        }

    def to_markdown(self) -> str:
        p50, p95 = self.latency_percentiles()
        lines: list[str] = []
        lines.append("# Agent harness scorecard\n")
        lines.append(
            f"**{self.passed_count}/{self.total} scenarios passed** "
            f"({self.pass_rate:.0%}) -- p50 {p50:.0f} ms -- p95 {p95:.0f} ms\n"
        )

        lines.append("## Per-metric accuracy\n")
        lines.append("| Metric | Mean score | Scenarios |")
        lines.append("| --- | --- | --- |")
        for name, (mean, n) in sorted(self.per_metric_accuracy().items()):
            lines.append(f"| {name} | {mean:.2f} | {n} |")
        lines.append("")

        lines.append("## Scenarios\n")
        lines.append("| Scenario | Result | Latency | Failed metrics |")
        lines.append("| --- | --- | --- | --- |")
        for r in self.reports:
            status = "PASS" if r.passed else "FAIL"
            failed = ", ".join(
                m.name for m in r.metrics if m.passed is False
            ) or "-"
            lines.append(
                f"| {r.scenario_id} | {status} | {r.latency_ms:.0f} ms | {failed} |"
            )
        lines.append("")
        return "\n".join(lines)
