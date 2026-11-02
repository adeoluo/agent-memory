# Definition of Done

> Per-project checklist derived from the portfolio-wide standard.
> A PR is mergeable only when every applicable box is checked.

## Engineering
- [x] Core logic built from scratch; frameworks justified in README.
- [x] Typed, modular, no god-files. ADR added for non-obvious decisions.

## CI/CD
- [x] `make all` passes locally (format · lint · type · test).
- [x] CI green on PR; coverage gate 90% (measured 98%).
- [x] One-command run (`make run` serves MCP) + Docker build works.

## Diagram
- [x] Architecture diagram present, **centered title**, shared palette, legend.
- [x] `.mmd` source + rendered `.svg` committed; embedded in README.

## Documentation
- [x] README: motivation · diagram · results table · design · limitations · roadmap.
- [x] Demonstration: command-line transcript in the README.

## Evidence
- [x] Results table with numbers versus baselines.
- [x] Multiple seeds + error bars / CI.
- [x] Reproducible via `make evaluation`; raw numbers in `benchmarks/results.json`.

## Responsible AI
- [x] Model card, data card, threat model current.

## Security
- [x] No secrets in history; CodeQL + gitleaks pass.

## Hygiene
- [x] Conventional commits; LICENSE, CITATION, CONTRIBUTING present.
- [x] Release v0.1.0 with wheel and source distribution attached.
