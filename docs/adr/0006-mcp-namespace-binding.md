# ADR-0006: The MCP server is bound to one namespace at start-up

- **Status:** Accepted
- **Date:** 2026-11-01

## Context
The MCP server hands memory tools to a language model. Tool arguments are chosen by the model and
can be influenced by untrusted content (prompt injection). If a tool accepted a namespace
argument, an injected instruction could read or delete another user's memories.

## Decision
`agent-memory mcp` takes the database and namespace from the command line or environment and
builds the server around a single `AgentMemory` instance. The tools (`remember`, `recall`,
`forget`, `list_facts`) have no namespace parameter. `forget` deletes only within that namespace
and reports `forgotten: false` for identifiers that belong elsewhere. `recall` caps `k` at 50.
The server uses the official `mcp` Python SDK (`MCPServer`) over standard input and output.

## Consequences
- Isolation is enforced by construction and tested (an identifier from another namespace cannot
  be deleted through the server).
- Serving several users requires one server process per namespace, which matches how desktop MCP
  clients launch servers anyway.
- A model can still store false statements about its own user. Recalled memories are data, not
  instructions; clients should present them to the model as quoted context.
