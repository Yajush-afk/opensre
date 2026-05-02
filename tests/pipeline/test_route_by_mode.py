from __future__ import annotations

import logging
from typing import Any, cast

import pytest

from app.pipeline.routing import route_by_mode
from app.state import AgentState


@pytest.mark.parametrize(
    ("state", "expected_route"),
    [
        ({"mode": "investigation"}, "investigation"),
        ({"mode": "chat"}, "chat"),
    ],
)
def test_route_by_mode_valid_modes_do_not_warn(
    state: dict[str, Any],
    expected_route: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.pipeline.routing"):
        assert route_by_mode(cast(AgentState, state)) == expected_route

    assert not caplog.records


@pytest.mark.parametrize("state", [{}, {"mode": None}])
def test_route_by_mode_missing_or_none_mode_warns_and_defaults_to_chat(
    state: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.pipeline.routing"):
        assert route_by_mode(cast(AgentState, state)) == "chat"

    assert any("mode is missing or None" in record.message for record in caplog.records)


def test_route_by_mode_unrecognized_mode_warns_and_defaults_to_chat(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.pipeline.routing"):
        assert route_by_mode(cast(AgentState, {"mode": "invalid"})) == "chat"

    assert any("unrecognized mode 'invalid'" in record.message for record in caplog.records)
