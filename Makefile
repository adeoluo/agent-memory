.PHONY: help setup lint format type test coverage evaluation run diagram docker-build docker-up clean all build changelog cut-release

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies and pre-commit hooks
	uv sync --all-extras --dev
	uv run pre-commit install

format: ## Format automatically
	uv run ruff format .
	uv run ruff check --fix .

lint: ## Lint (no fixes)
	uv run ruff format --check .
	uv run ruff check .

type: ## Type-check
	uv run mypy src tests

test: ## Run tests
	uv run pytest

coverage: ## Tests with coverage gate
	uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

evaluation: ## Reproduce the results tables (benchmarks/results.md)
	uv run python benchmarks/run_benchmark.py

run: ## Serve the Model Context Protocol server on standard input and output
	uv run agent-memory mcp

diagram: ## Render architecture diagram to SVG
	npx -y @mermaid-js/mermaid-cli -i docs/architecture/architecture.mmd \
	     -o docs/architecture/architecture.svg \
	     -c mermaid.config.json -b transparent

docker-build: ## Build the image
	docker build -t agent-memory .

docker-up: ## Build and start the MCP server container
	docker compose up --build

clean: ## Remove caches and artifacts
	rm -rf .pytest_cache .pytest-tmp .mypy_cache .ruff_cache dist build *.egg-info coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +

all: lint type coverage ## Full local gate (mirror of continuous integration)

build: ## Build the wheel and source distribution into dist/
	uv build

changelog: ## Regenerate CHANGELOG.md from Conventional Commits (git-cliff)
	git cliff --output CHANGELOG.md && perl -0pi -e 's/\n+\z/\n/' CHANGELOG.md

cut-release: ## Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional)
	scripts/release.sh $(RELEASE_VERSION)
