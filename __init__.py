"""Route6 plugin for Hermes Agent — https://route6.me

Gives the agent a real public IPv6 identity, DNS hostname, port
forwarding, outbound web tools (fetch/search/browse/scrape), and — on
Team plans — a private mesh with coordination tools (chat, whiteboard,
task queue, roles).

This plugin is a thin dynamic proxy: at startup it asks the Route6
gateway (``gw.route6.me/mcp``) for its current tool list and registers
every tool with the server-provided schema. Tool calls are forwarded to
the gateway over the MCP streamable-HTTP transport. Nothing is
reimplemented locally, so new Route6 tools appear here automatically —
no plugin update needed. If the gateway is unreachable at startup, a
bundled snapshot of the tool list is used instead (calls still go live).

Requires ``ROUTE6_API_KEY`` — free account at https://route6.me.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from .mcp_client import Route6MCP, Route6MCPError

logger = logging.getLogger(__name__)

_PLUGIN_DIR = Path(__file__).parent
_SNAPSHOT = _PLUGIN_DIR / "tools_snapshot.json"

_TOOLSET = "route6"
_EMOJI = "🌐"

# Hermes built-ins we must never name-collide with. Registration order differs
# between Hermes processes (dashboard loads built-ins before plugins, the
# gateway loads plugins first) — if we win the race under the bare name, the
# BUILT-IN gets rejected instead of us. Always register these prefixed.
_ALWAYS_PREFIX = {"web_search", "web_fetch", "scrape", "web_browse"}

_client: Route6MCP | None = None


def _get_client() -> Route6MCP:
    global _client
    if _client is None:
        _client = Route6MCP(api_key=os.environ["ROUTE6_API_KEY"])
    return _client


def _check_available() -> bool:
    return bool(os.environ.get("ROUTE6_API_KEY"))


def _discover_tools() -> list[dict]:
    """Live tools/list from the gateway; bundled snapshot as fallback."""
    try:
        tools = _get_client().tools_list()
        if tools:
            return tools
    except (Route6MCPError, Exception) as e:  # noqa: BLE001 — never block startup
        logger.warning("route6: live tool discovery failed (%s); using bundled snapshot", e)
    with open(_SNAPSHOT, encoding="utf-8") as f:
        return json.load(f)["tools"]


def _make_handler(tool_name: str):
    def handler(args: dict, **kwargs) -> str:
        try:
            return _get_client().tools_call(tool_name, args or {})
        except Route6MCPError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:  # noqa: BLE001 — handlers must never raise
            return json.dumps({"error": f"route6 {tool_name} failed: {e}"})

    return handler


def _register_one(ctx, name: str, description: str, parameters: dict, gateway_name: str) -> None:
    ctx.register_tool(
        name=name,
        toolset=_TOOLSET,
        schema={"name": name, "description": description, "parameters": parameters},
        handler=_make_handler(gateway_name),
        check_fn=_check_available,
        requires_env=["ROUTE6_API_KEY"],
        emoji=_EMOJI,
    )


def register(ctx) -> None:
    for tool in _discover_tools():
        name = tool["name"]
        description = tool.get("description", "")
        parameters = tool.get("inputSchema") or {"type": "object", "properties": {}}
        if name in _ALWAYS_PREFIX:
            alias = f"route6_{name}"
            try:
                _register_one(
                    ctx, alias,
                    f"{description} (Route6's {name} — prefixed so it never "
                    f"collides with the built-in tool of the same name; this "
                    f"one runs through your Route6 network identity.)",
                    parameters, gateway_name=name,
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("route6: could not register tool %s: %s", alias, e)
            continue
        try:
            _register_one(ctx, name, description, parameters, gateway_name=name)
        except Exception:
            # Name shadows a built-in tool (e.g. Hermes' own web_search).
            # Re-register under a route6_ prefix — the handler still calls
            # the gateway by the ORIGINAL name. Never let one tool (or the
            # skill) abort plugin load / session startup.
            alias = f"route6_{name}"
            try:
                _register_one(
                    ctx, alias,
                    f"{description} (Route6's {name} — prefixed because a "
                    f"built-in tool already uses that name; this one runs "
                    f"through your Route6 network identity.)",
                    parameters, gateway_name=name,
                )
                logger.info("route6: %s shadows a built-in tool; registered as %s", name, alias)
            except Exception as e:  # noqa: BLE001
                logger.warning("route6: could not register tool %s: %s", name, e)

    try:
        skill_md = _PLUGIN_DIR / "skills" / "route6" / "SKILL.md"
        if skill_md.exists():
            ctx.register_skill(
                "route6",
                skill_md,
                description="How to use Route6 network tools: identity, hostname, "
                "port forwarding, web fetch/search/scrape, team mesh coordination.",
            )
    except Exception as e:  # noqa: BLE001
        logger.warning("route6: skill registration failed: %s", e)
