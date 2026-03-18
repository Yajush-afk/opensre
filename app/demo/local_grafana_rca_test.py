from __future__ import annotations

from app.demo.local_grafana_rca import DEFAULT_FIXTURE_PATH, load_demo_fixture, prepare_demo_state


def test_load_grafana_demo_fixture_reads_alert_and_evidence() -> None:
    fixture = load_demo_fixture(DEFAULT_FIXTURE_PATH)

    assert fixture["alert"]["title"]
    assert fixture["evidence"]["grafana_error_logs"]


def test_prepare_grafana_demo_state_sets_grafana_context() -> None:
    fixture = load_demo_fixture(DEFAULT_FIXTURE_PATH)

    state = prepare_demo_state(fixture)

    assert state["alert_source"] == "grafana"
    assert state["pipeline_name"] == "events_fact"
    assert state["available_sources"]["grafana"]["grafana_endpoint"] == "https://tracerbio.grafana.net"
    assert state["evidence"]["grafana_logs_service"] == "prefect-etl-pipeline"
    assert "Error: Table events_fact has not been updated in over 2 hours" in state["problem_md"]
