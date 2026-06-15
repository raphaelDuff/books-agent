"""Pytest gate over the harness scenarios.

One parametrized test per scenario drives the full compiled graph and asserts
every metric the scenario declares. A broken path shows up as a single readable
red line naming the scenario and the failed metrics. Fully hermetic — scripted
fakes only, zero network.
"""

import pytest

from tests.harness.engine import evaluate, run_scenario
from tests.harness.scenarios import SCENARIOS


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s.id)
async def test_scenario(scenario):
    report = await evaluate(scenario)
    failed = [
        f"{m.name}: {m.detail}" for m in report.metrics if m.passed is False
    ]
    assert not failed, f"{scenario.id} failed:\n  " + "\n  ".join(failed)


async def test_hybrid_passes_allowlist_to_vector_search():
    """Distinctive HYBRID behaviour: the SQL result set becomes the vector
    search allowlist (not covered by the generic metrics)."""
    scenario = next(s for s in SCENARIOS if s.id == "hybrid_sql_then_semantic")
    result = await run_scenario(scenario)
    assert result.deps.vector_repo.last_allowlist == ["111", "222"]


async def test_semantic_uses_no_allowlist():
    scenario = next(s for s in SCENARIOS if s.id == "semantic_only")
    result = await run_scenario(scenario)
    assert result.deps.vector_repo.last_allowlist is None
