"""Compatibility shim so Ragas imports under langchain 1.x.

Ragas 0.4.3 (the latest release) eagerly does, at package import:

    from langchain_community.chat_models.vertexai import ChatVertexAI

but ``langchain-community`` 0.4.2 — the version compatible with the
``langchain-core`` 1.x this project requires — removed that module (Vertex AI
moved to its own package long ago). Older community versions that still ship it
pin ``langchain-core <1``, which the app can't use. So there is no single
version set where stock Ragas imports cleanly here.

We only ever drive Ragas with OpenAI, so ``ChatVertexAI`` is never instantiated
— Ragas merely references it in an ``isinstance`` allow-list. We register a stub
module for the removed path *before* importing Ragas. Import this module first:

    from tests.harness import _ragas_compat  # noqa: F401  (registers the shim)
    from ragas import SingleTurnSample

Remove once Ragas ships a release that no longer eager-imports the Vertex path.
"""

from __future__ import annotations

import sys
import types

_MISSING = "langchain_community.chat_models.vertexai"

if _MISSING not in sys.modules:
    try:  # if the real module ever returns, prefer it
        __import__(_MISSING)
    except ModuleNotFoundError:
        stub = types.ModuleType(_MISSING)

        class ChatVertexAI:  # placeholder; never instantiated in this project
            """Stub for the removed langchain-community Vertex chat model."""

        stub.ChatVertexAI = ChatVertexAI  # type: ignore[attr-defined]
        sys.modules[_MISSING] = stub
