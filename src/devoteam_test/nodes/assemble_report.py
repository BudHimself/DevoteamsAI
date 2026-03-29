from devoteam_test.models.anomaly import Anomaly
from devoteam_test.models.report import LineReport
from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.nodes.recommendations import _rule_messages
from devoteam_test.state import GraphState


def assemble_report(state: GraphState) -> dict[str, object]:
    snap = MetricSnapshot.model_validate(state.snapshot)
    anomalies = [Anomaly.model_validate(a) for a in state.anomalies]
    recs = list(state.recommendations)
    rule_based = _rule_messages(snap, anomalies)
    summary = state.summary
    src = state.recommendation_source

    line = LineReport(
        timestamp=snap.timestamp,
        anomalies=anomalies,
        recommendations=recs,
        rule_based_recommendations=rule_based,
        summary=summary,
        recommendation_source=src,
    )
    return {"line_report": line.model_dump(mode="json")}
