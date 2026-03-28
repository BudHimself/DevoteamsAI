import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from devoteam_test.config_loader import load_thresholds
from devoteam_test.graph import build_graph
from devoteam_test.models.report import AggregatedPipelineOutput, LineReport
from devoteam_test.state import GraphState

logger = logging.getLogger(__name__)


def _state_from_invoke(result: object) -> GraphState:
    if isinstance(result, GraphState):
        return result
    if isinstance(result, dict):
        return GraphState.model_validate(result)
    msg = f"Sortie de graphe inattendue : {type(result)!r}"
    raise TypeError(msg)


def _default_paths() -> tuple[Path, Path]:
    root = Path.cwd()
    rapport = Path(os.environ.get("RAPPORT_PATH", root / "rapport.json"))
    thresholds = Path(os.environ.get("THRESHOLDS_PATH", root / "config" / "thresholds.yaml"))
    return rapport, thresholds


def _global_summary(reports: list[LineReport]) -> str:
    n = len(reports)
    total = sum(len(r.anomalies) for r in reports)
    llm_rows = sum(1 for r in reports if r.recommendation_source == "llm")
    return (
        f"{n} mesure(s) traitée(s) ; {total} anomalie(s) cumulées ; "
        f"{llm_rows} ligne(s) avec recommandations issues du LLM."
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv()
    if not os.environ.get("OPENROUTER_API_KEY", "").strip():
        logger.info(
            "OPENROUTER_API_KEY non défini : les lignes avec >1 anomalie "
            "utiliseront le repli déterministe (sans appel LLM).",
        )

    rapport_path, thresholds_path = _default_paths()
    raw = json.loads(rapport_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        logger.error("Le fichier rapport doit contenir un tableau JSON.")
        sys.exit(1)

    thresholds = load_thresholds(thresholds_path)
    graph = build_graph(thresholds)

    reports: list[LineReport] = []
    for row in raw:
        if not isinstance(row, dict):
            logger.error("Chaque entrée du rapport doit être un objet JSON.")
            sys.exit(1)
        out = graph.invoke(GraphState(snapshot=row))
        final = _state_from_invoke(out)
        lr = final.line_report
        if lr is None:
            logger.error("Sortie du graphe invalide : line_report manquant.")
            sys.exit(1)
        reports.append(LineReport.model_validate(lr))

    agg = AggregatedPipelineOutput(reports=reports, global_summary=_global_summary(reports))
    sys.stdout.write(agg.model_dump_json(indent=2, ensure_ascii=False))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
