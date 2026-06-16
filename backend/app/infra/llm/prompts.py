"""Loader for the versioned LLM prompts in ``prompts.yaml``.

Keeps prompt text out of the adapter code: prompts can be reviewed, diffed and
versioned on their own. This is an ``infra/llm`` detail — nothing inner depends
on it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Graph nodes that read a system prompt from the YAML file.
REQUIRED_NODES = ("classify_intent", "repair_sql", "rank")

_DEFAULT_PATH = Path(__file__).parent / "prompts.yaml"


class PromptLibrary:
    """Versioned system prompts, keyed by graph-node name.

    Construct via :meth:`from_yaml` (loads the co-located ``prompts.yaml`` by
    default). Injectable into ``OpenAILLMService`` so tests can supply their own.
    """

    def __init__(self, nodes: dict[str, dict[str, Any]]) -> None:
        self._nodes = nodes
        self._validate()

    @classmethod
    def from_yaml(cls, path: Path | None = None) -> "PromptLibrary":
        """Load prompts from ``path`` (defaults to the co-located file).

        The path is resolved from this module's directory, so it works regardless
        of the current working directory.
        """
        source = path or _DEFAULT_PATH
        data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        nodes = data.get("nodes") or {}
        return cls(nodes)

    def _validate(self) -> None:
        for node in REQUIRED_NODES:
            entry = self._nodes.get(node)
            if not entry:
                raise ValueError(f"prompts.yaml: missing node '{node}'")
            if not (entry.get("system_prompt") or "").strip():
                raise ValueError(f"prompts.yaml: node '{node}' has no system_prompt")
            if not (entry.get("version") or "").strip():
                raise ValueError(f"prompts.yaml: node '{node}' has no version")

    def system(self, node: str) -> str:
        """The system prompt for ``node`` (stripped of trailing whitespace)."""
        return self._nodes[node]["system_prompt"].strip()

    def version(self, node: str) -> str:
        """The semver string for ``node``'s prompt."""
        return self._nodes[node]["version"]

    def versions(self) -> dict[str, str]:
        """Map of node name -> prompt version (for logging / provenance)."""
        return {node: entry["version"] for node, entry in self._nodes.items()}
