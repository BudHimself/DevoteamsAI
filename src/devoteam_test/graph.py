from typing import Any

from langgraph.graph import END, START, StateGraph

from devoteam_test.nodes.assemble_report import assemble_report
from devoteam_test.nodes.detect import make_detect_node
from devoteam_test.nodes.ingest import ingest_node
from devoteam_test.nodes.recommendations import (
    make_llm_node,
    make_rules_node,
    route_after_detect,
)
from devoteam_test.state import GraphState
from devoteam_test.thresholds_schema import ThresholdConfig


def build_graph(thresholds: ThresholdConfig) -> Any:
    graph = StateGraph(GraphState)
    graph.add_node("ingest", ingest_node)
    graph.add_node("detect", make_detect_node(thresholds))
    graph.add_node("llm", make_llm_node(thresholds))
    graph.add_node("rules", make_rules_node(thresholds))
    graph.add_node("report", assemble_report)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "detect")
    graph.add_conditional_edges(
        "detect",
        route_after_detect,
        {"llm": "llm", "rules": "rules"},
    )
    graph.add_edge("llm", "report")
    graph.add_edge("rules", "report")
    graph.add_edge("report", END)

    return graph.compile()
