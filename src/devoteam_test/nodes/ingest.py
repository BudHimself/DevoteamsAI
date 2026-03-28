from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.state import GraphState


def ingest_node(state: GraphState) -> dict[str, object]:
    snap = MetricSnapshot.model_validate(state.snapshot)
    return {"snapshot": snap.model_dump(mode="json")}
