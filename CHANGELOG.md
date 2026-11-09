# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## [0.1.1] 2026-11-09

### Bug fixes

- Current Claude model and Messages API version, with a request shape test (#10)

### Documentation

- Standard README structure and architecture diagram
- Vertical layered architecture diagram
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram
- Remove authorship statements from docs and scripts
- Recorded demos of more commands, with their vhs tapes (#3)
- Recorded demos of the HTTP service and more commands (#4)
- Complete citation metadata and bump it on release (#6)
- Render every architecture diagram in the house style (#8)
- Diagrams on white in the shared theme, make diagram for every diagram, and a self-contained Definition of Done (#9)

### Build and CI

- Run CodeQL on main and on a weekly schedule only
- Build and attach the sdist and wheel to every release (#11)

### Maintenance

- Add release automation, AGENTS.md, llms.txt and contributor docs
- Classify squash merges in the changelog by the commits they contain
- Latest toolchain and CI versions (#5)
- Release script keeps hard-coded version strings in step (#7)

## [0.1.0] 2026-11-02

### Features

- Long-term memory system for AI agents

### Maintenance

- Initialize repository
