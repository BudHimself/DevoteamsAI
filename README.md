# devoteam-test

Ce dépôt est une **réponse au test technique d’embauche** proposé par **Devoteam AI**. Il illustre une petite application Python structurée autour d’un pipeline **LangGraph** pour traiter des métriques d’infrastructure simulées.

**Objectif :** ingérer des mesures au format JSON, **détecter les anomalies** à partir de **seuils configurables** (fichier YAML), puis produire des **recommandations** exploitables. Lorsqu’une ligne ne présente qu’**une seule** anomalie (ou aucune), les conseils sont générés par des **règles métier déterministes** ; dès qu’**plusieurs** anomalies coexistent sur la même mesure, le contexte est envoyé à un **LLM** via **OpenRouter** pour une synthèse priorisée, avec repli sur les règles si besoin. Le résultat agrégé est écrit dans un fichier JSON (par défaut `output.json`).

Pour l’architecture détaillée, les variables d’environnement et les commandes : voir [`docs/pipeline-infrastructure.md`](docs/pipeline-infrastructure.md).

## Démarrage rapide

```bash
uv sync --all-groups
cp .env.example .env   # renseigner OPENROUTER_API_KEY si vous utilisez le LLM
make run               # ou : uv run devoteam-pipeline
```

Stack : Python 3.12, uv, Ruff, ty, LangGraph, LangChain (OpenRouter).
