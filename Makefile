.DEFAULT_GOAL := help

UV ?= uv

.PHONY: help
help: ## Afficher les cibles Make disponibles
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: sync
sync: ## Installer les dépendances (uv sync)
	$(UV) sync --all-groups

.PHONY: run
run: ## Exécuter le pipeline (sortie dans OUTPUT_PATH, défaut pipeline_output.json)
	$(UV) run devoteam-pipeline

.PHONY: lint
lint: ## Vérifier le style et les erreurs (ruff check)
	$(UV) run ruff check src

.PHONY: format
format: ## Formater le code (ruff format)
	$(UV) run ruff format src

.PHONY: typecheck
typecheck: ## Analyse statique des types (ty)
	$(UV) run ty check src

.PHONY: check
check: lint typecheck ## Lint + typage
