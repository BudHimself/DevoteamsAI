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


def _resolve_output_destination() -> Path | None:
    raw = os.environ.get("OUTPUT_PATH")
    if raw is None:
        return Path.cwd() / "output.json"
    stripped = raw.strip()
    if stripped == "-":
        return None
    return Path(stripped)


def _global_summary(rows_analyzed: int, reports: list[LineReport]) -> str:
    n_reports = len(reports)
    nominal = rows_analyzed - n_reports
    total = sum(len(r.anomalies) for r in reports)
    llm_rows = sum(1 for r in reports if r.recommendation_source == "llm")
    rules_rows = sum(1 for r in reports if r.recommendation_source == "rules")
    other_rows = n_reports - llm_rows - rules_rows
    base = (
        f"{rows_analyzed} mesure(s) lues ; {n_reports} ligne(s) avec anomalie(s) "
        f"({nominal} ligne(s) nominale(s) exclues de la sortie) ; "
        f"{total} anomalie(s) cumulée(s) ; "
        f"{rules_rows} ligne(s) dont les recommandations proviennent des règles métier ;"
        f"{llm_rows} ligne(s) dont les recommandations proviennent du LLM."
    )
    if other_rows:
        return (
            f"{base} ({other_rows} ligne(s) avec recommendation_source inattendu "
            f"(hors llm/rules), à vérifier.)"
        )
    return base


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
    rows_analyzed = 0
    for row in raw:
        if not isinstance(row, dict):
            logger.error("Chaque entrée du rapport doit être un objet JSON.")
            sys.exit(1)
        rows_analyzed += 1
        out = graph.invoke(GraphState(snapshot=row))
        final = _state_from_invoke(out)
        lr = final.line_report
        if lr is None:
            logger.error("Sortie du graphe invalide : line_report manquant.")
            sys.exit(1)
        line_report = LineReport.model_validate(lr)
        if line_report.anomalies:
            reports.append(line_report)

    agg = AggregatedPipelineOutput(
        rows_analyzed=rows_analyzed,
        reports=reports,
        global_summary=_global_summary(rows_analyzed, reports),
    )
    payload = agg.model_dump_json(indent=2, ensure_ascii=False) + "\n"
    out_dest = _resolve_output_destination()
    if out_dest is None:
        sys.stdout.write(payload)
    else:
        out_dest.parent.mkdir(parents=True, exist_ok=True)
        out_dest.write_text(payload, encoding="utf-8")
        logger.info("Rapport écrit dans %s", out_dest.resolve())


if __name__ == "__main__":
    main()
