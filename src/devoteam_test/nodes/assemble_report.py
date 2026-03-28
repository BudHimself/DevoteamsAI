from devoteam_test.models.anomaly import Anomaly
from devoteam_test.models.report import LineReport
from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.state import GraphState


def assemble_report(state: GraphState) -> dict[str, object]:
    snap = MetricSnapshot.model_validate(state.snapshot)
    anomalies = [Anomaly.model_validate(a) for a in state.anomalies]
    recs = list(state.recommendations)
    summary = state.summary
    src = state.recommendation_source

    line = LineReport(
        timestamp=snap.timestamp,
        anomalies=anomalies,
        recommendations=recs,
        summary=summary,
        recommendation_source=src,
    )
    return {"line_report": line.model_dump(mode="json")}
