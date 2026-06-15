"""Testing harness for the LangGraph books agent.

Drives the *full compiled graph* through reproducible, declaratively-defined
scenarios with scripted, hermetic dependencies, and scores each run into a
metrics scorecard. See ``backend/tests/harness/README`` notes in the project
README ("Testing the agent").

Layers
------
- Deterministic (default): scripted fakes, zero network — the CI gate.
- Live eval (opt-in, ``RUN_LIVE_EVAL=1``): real models + DBs, Ragas RAG-quality
  metrics. Lives in :mod:`tests.test_live_eval`, not imported here.
"""
