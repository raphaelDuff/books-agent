"""Automatic evaluation metrics.

Each metric is a pure function ``(Scenario, RunResult) -> MetricResult``. When
the scenario does not assert a dimension (the relevant ``expect_*`` is ``None``)
the metric returns ``score=None, passed=None`` and is skipped — it neither
fails nor counts toward accuracy. Register a new metric by writing one function
and adding it to ``METRICS``.
"""

from __future__ import annotations

from tests.harness.types import MetricResult, RunResult, Scenario


# sentinel skip result
def _skip(name: str) -> MetricResult:
    return MetricResult(name=name, score=None, passed=None, detail="not asserted")


def intent_correct(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_intent is None:
        return _skip("intent_correct")
    got = r.output.get("intent")
    ok = got == s.expect_intent
    return MetricResult(
        name="intent_correct",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"expected {s.expect_intent!r}, got {got!r}",
    )


def route_correct(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_route is None:
        return _skip("route_correct")
    ok = r.route == s.expect_route
    return MetricResult(
        name="route_correct",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"expected {list(s.expect_route)}, got {list(r.route)}",
    )


def retrieval_recall(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_recall_isbns is None:
        return _skip("retrieval_recall")
    want = s.expect_recall_isbns
    found = want & set(r.pick_isbns)
    score = len(found) / len(want) if want else 1.0
    return MetricResult(
        name="retrieval_recall",
        score=score,
        passed=score == 1.0,
        detail=f"{len(found)}/{len(want)} expected ISBNs in picks",
    )


def pick_precision(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_pick_isbns is None:
        return _skip("pick_precision")
    ok = tuple(r.pick_isbns) == s.expect_pick_isbns
    return MetricResult(
        name="pick_precision",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"expected {list(s.expect_pick_isbns)}, got {r.pick_isbns}",
    )


def sql_retry_correct(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_sql_attempts is None:
        return _skip("sql_retry_correct")
    # attempts = initial sql_search + one per repair; repairs == attempts - 1
    expected_repairs = s.expect_sql_attempts - 1
    got_repairs = r.deps.llm.repair_calls
    ok = got_repairs == expected_repairs
    return MetricResult(
        name="sql_retry_correct",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"expected {expected_repairs} repair(s), got {got_repairs}",
    )


def generated_sql_correct(s: Scenario, r: RunResult) -> MetricResult:
    if s.expect_generated_sql is None:
        return _skip("generated_sql_correct")
    present = bool(r.output.get("generated_sql"))
    ok = present == s.expect_generated_sql
    return MetricResult(
        name="generated_sql_correct",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"expected present={s.expect_generated_sql}, got present={present}",
    )


def dedup_correct(s: Scenario, r: RunResult) -> MetricResult:
    """Picks must contain no duplicate ISBNs (always checked when picks exist)."""
    isbns = r.pick_isbns
    if not isbns:
        return _skip("dedup_correct")
    ok = len(isbns) == len(set(isbns))
    return MetricResult(
        name="dedup_correct",
        score=1.0 if ok else 0.0,
        passed=ok,
        detail=f"{len(isbns)} picks, {len(set(isbns))} unique",
    )


def latency(s: Scenario, r: RunResult) -> MetricResult:
    """Informational only — never gates (keeps the harness machine-independent)."""
    return MetricResult(
        name="latency_ms",
        score=None,
        passed=None,
        detail=f"{r.latency_ms:.1f} ms",
    )


METRICS = (
    intent_correct,
    route_correct,
    retrieval_recall,
    pick_precision,
    sql_retry_correct,
    generated_sql_correct,
    dedup_correct,
    latency,
)
