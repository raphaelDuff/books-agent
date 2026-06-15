"""Build a :class:`Scorecard` by evaluating a list of scenarios.

The aggregation/rendering lives on :class:`tests.harness.types.Scorecard`; this
module just orchestrates the runs. Kept separate from the pytest gate so both
the gate and the CLI runner share one path to a scorecard.
"""

from __future__ import annotations

import asyncio
from typing import Sequence

from tests.harness.engine import evaluate
from tests.harness.types import Scenario, Scorecard


async def build_scorecard(scenarios: Sequence[Scenario]) -> Scorecard:
    reports = [await evaluate(s) for s in scenarios]
    return Scorecard(reports=reports)


def build_scorecard_sync(scenarios: Sequence[Scenario]) -> Scorecard:
    return asyncio.run(build_scorecard(scenarios))
