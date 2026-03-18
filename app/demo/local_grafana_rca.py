"""Run a bundled local Grafana RCA demo with sample alert and evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

from dotenv import load_dotenv

load_dotenv(override=False)

from app.agent.nodes.publish_findings.node import generate_report  # noqa: E402
from app.agent.nodes.root_cause_diagnosis.node import diagnose_root_cause  # noqa: E402
from app.agent.state import InvestigationState, make_initial_state  # noqa: E402
from app.demo.local_rca import load_demo_fixture, require_llm_config  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_PATH = REPO_ROOT / "app" / "demo" / "fixtures" / "local_grafana_rca.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bundled local Grafana RCA example and render the report."
    )
    parser.add_argument(
        "--fixture",
        default=str(DEFAULT_FIXTURE_PATH),
        help="Path to a bundled Grafana alert+evidence fixture JSON file.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to write the rendered RCA report as Markdown.",
    )
    return parser.parse_args(argv)


def prepare_demo_state(fixture: dict[str, Any]) -> InvestigationState:
    alert = cast(dict[str, Any], fixture["alert"])
    evidence = cast(dict[str, Any], fixture["evidence"])
    meta = cast(dict[str, Any], fixture.get("_meta", {}))

    common_labels = cast(dict[str, Any], alert.get("commonLabels", {}))
    common_annotations = cast(dict[str, Any], alert.get("commonAnnotations", {}))

    alert_name = str(alert.get("title") or common_labels.get("alertname") or "Bundled Grafana RCA Demo")
    pipeline_name = str(
        common_labels.get("pipeline_name")
        or common_labels.get("table")
        or common_labels.get("grafana_folder")
        or "unknown"
    )
    severity = str(common_labels.get("severity") or "critical")
    error_message = str(common_annotations.get("summary") or "")
    source_url = str(common_annotations.get("source_url") or alert.get("externalURL") or "")

    state = make_initial_state(
        alert_name=alert_name,
        pipeline_name=pipeline_name,
        severity=severity,
        raw_alert={
            **alert,
            "alert_source": "grafana",
            "error_message": error_message,
            "source_url": source_url,
        },
    )
    state["problem_md"] = build_problem_md(
        alert_name=alert_name,
        pipeline_name=pipeline_name,
        severity=severity,
        error_message=error_message,
    )
    state["alert_source"] = "grafana"
    state["evidence"] = evidence
    state["available_sources"] = {
        "grafana": {
            "grafana_endpoint": str(meta.get("grafana_endpoint") or "https://tracerbio.grafana.net")
        }
    }
    return state


def build_problem_md(
    *,
    alert_name: str,
    pipeline_name: str,
    severity: str,
    error_message: str,
) -> str:
    parts = [f"# {alert_name}", f"Pipeline: {pipeline_name} | Severity: {severity}"]
    if error_message:
        parts.append(f"\nError: {error_message}")
    return "\n".join(parts)


def run_demo(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    require_llm_config("make local-grafana-demo")

    fixture = load_demo_fixture(Path(args.fixture))
    state = prepare_demo_state(fixture)

    diagnosis = diagnose_root_cause(state)
    state.update(diagnosis)

    report = generate_report(state)["slack_message"]
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    run_demo(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
