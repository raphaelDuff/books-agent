"""CLI runner: evaluate all scenarios and emit a human-readable scorecard.

    uv run python -m tests.harness.run

Prints a markdown scorecard to stdout and writes ``scorecard.json`` next to the
backend root. Exits non-zero if any scenario fails, so it can double as a gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tests.harness.scenarios import SCENARIOS
from tests.harness.scorecard import build_scorecard_sync

OUTPUT_JSON = Path(__file__).resolve().parents[2] / "scorecard.json"


def main() -> int:
    scorecard = build_scorecard_sync(SCENARIOS)

    print(scorecard.to_markdown())

    OUTPUT_JSON.write_text(
        json.dumps(scorecard.to_dict(), indent=2), encoding="utf-8"
    )
    print(f"\nWrote {OUTPUT_JSON}")

    return 0 if scorecard.passed_count == scorecard.total else 1


if __name__ == "__main__":
    sys.exit(main())
