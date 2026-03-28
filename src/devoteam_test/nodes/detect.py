from devoteam_test.detection import detect_anomalies
from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.state import GraphState
from devoteam_test.thresholds_schema import ThresholdConfig


def make_detect_node(thresholds: ThresholdConfig):
    def detect_node(state: GraphState) -> dict[str, object]:
        snap = MetricSnapshot.model_validate(state.snapshot)
        found = detect_anomalies(snap, thresholds)
        return {"anomalies": [a.model_dump(mode="json") for a in found]}

    return detect_node
