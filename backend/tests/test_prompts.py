"""The prompt library loads, exposes every node, and validates its inputs."""

import re

import pytest

from app.infra.llm.prompts import REQUIRED_NODES, PromptLibrary

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_default_yaml_loads_all_nodes():
    lib = PromptLibrary.from_yaml()
    for node in REQUIRED_NODES:
        assert lib.system(node).strip(), f"{node} has an empty system prompt"
        assert _SEMVER.match(lib.version(node)), f"{node} version is not semver"


def test_versions_covers_required_nodes():
    versions = PromptLibrary.from_yaml().versions()
    assert set(REQUIRED_NODES) <= set(versions)


def test_missing_node_raises():
    with pytest.raises(ValueError, match="missing node 'rank'"):
        PromptLibrary(
            {
                "classify_intent": {"version": "1.0.0", "system_prompt": "x"},
                "repair_sql": {"version": "1.0.0", "system_prompt": "x"},
            }
        )


def test_missing_version_raises():
    with pytest.raises(ValueError, match="no version"):
        PromptLibrary(
            {
                "classify_intent": {"system_prompt": "x"},
                "repair_sql": {"version": "1.0.0", "system_prompt": "x"},
                "rank": {"version": "1.0.0", "system_prompt": "x"},
            }
        )
