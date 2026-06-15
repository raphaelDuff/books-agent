"""The harness core: drive the *full compiled graph* for one scenario.

``run_scenario`` streams the graph so we observe the exact node-visit order
(``stream_mode="updates"`` yields one chunk per node, keyed by node name —
including a repeated ``sql_search`` when a repair loops back). ``evaluate``
then applies every registered metric to produce a :class:`ScenarioReport`.
"""

from __future__ import annotations

import time

from app.agent.graph import build_graph
from tests.harness.fakes import build_deps, cfg
from tests.harness.metrics import METRICS
from tests.harness.types import RunResult, Scenario, ScenarioReport


async def run_scenario(scenario: Scenario) -> RunResult:
    """Execute one scenario against a fresh compiled graph.

    A fresh ``build_graph()`` per run gives each scenario its own ``MemorySaver``,
    so checkpoint state never bleeds between scenarios.
    """
    graph = build_graph()
    deps = build_deps(scenario)
    config = cfg(thread_id=scenario.id, deps=deps)

    visited: list[str] = []
    start = time.perf_counter()
    async for chunk in graph.astream(
        {"question": scenario.question}, config, stream_mode="updates"
    ):
        # each chunk is {node_name: partial_state_update}; one per node execution
        visited.extend(chunk.keys())
    snapshot = await graph.aget_state(config)
    latency_ms = (time.perf_counter() - start) * 1000.0

    return RunResult(
        output=dict(snapshot.values),
        route=tuple(visited),
        latency_ms=latency_ms,
        deps=deps,
    )


async def evaluate(scenario: Scenario) -> ScenarioReport:
    """Run the scenario and score it with every registered metric."""
    result = await run_scenario(scenario)
    metrics = [metric(scenario, result) for metric in METRICS]
    return ScenarioReport(
        scenario_id=scenario.id,
        metrics=metrics,
        latency_ms=result.latency_ms,
    )
