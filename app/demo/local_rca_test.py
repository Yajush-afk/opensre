from __future__ import annotations

from app.demo.local_rca import DEFAULT_FIXTURE_PATH, load_demo_fixture, prepare_demo_state


def test_load_demo_fixture_reads_bundled_alert_and_evidence() -> None:
    fixture = load_demo_fixture(DEFAULT_FIXTURE_PATH)

    assert fixture["alert"]["title"]
    assert fixture["evidence"]["datadog_logs"]


def test_prepare_demo_state_populates_alert_and_evidence_context() -> None:
    fixture = load_demo_fixture(DEFAULT_FIXTURE_PATH)

    state = prepare_demo_state(fixture)

    assert state["alert_name"] == fixture["alert"]["title"]
    assert state["pipeline_name"] == "kubernetes_etl_pipeline"
    assert state["alert_source"] == "datadog"
    assert state["evidence"] == fixture["evidence"]
    assert state["available_sources"]["datadog"]["site"] == "datadoghq.com"
    assert "Namespace: tracer-test" in state["problem_md"]
