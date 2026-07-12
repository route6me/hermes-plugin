# Route6 plugin for Hermes Agent

Give your [Hermes Agent](https://github.com/NousResearch/hermes-agent) a real internet identity: a dedicated public **IPv6 /64**, an optional `*.on.route6.me` **DNS hostname**, inbound **port forwarding**, outbound **web fetch / search / browse / scrape** from a clean, stable IP — and, on Team plans, a **private mesh** with other agents plus coordination tools (chat, whiteboard, task queue, roles).

Powered by [Route6](https://route6.me) — the network layer for AI agents. Free tier available, no card required.

## Install

```bash
hermes plugins install route6me/hermes-plugin
```

The installer prompts for your `ROUTE6_API_KEY` — create a free account at **[route6.me](https://route6.me)** and copy the key from the dashboard. Then enable the plugin when prompted (or `hermes plugins enable route6`).

That's it. All Route6 tools appear in your agent's tool list on next startup.

## What your agent can do with it

| | Tools |
|--|--|
| **Identity** | `identity_get`, `identity_set_ipv6` (rotate/pin your IP), `identity_check_reputation` |
| **Network** | `net_ping`, `net_traceroute`, `net_dns_resolve` |
| **Web** | `web_fetch` (any URL, your own IP, optional JS render + screenshots), `web_search`, `web_browse`, `scrape` |
| **Inbound** | `hostname_register` (`you.on.route6.me`), `port_forward_create/delete/list`, `port_forward_tls`, `smtp_allowlist` |
| **Team mesh** | `team_status`, `team_ping`, `team_chat`, `team_whiteboard`, `team_task`, `team_capability`, `team_events`, `team_metrics`, `team_loop`, `team_project_task`, `team_roles` |
| **Account** | `plan_upgrade` |

Tool availability depends on your plan (Free: 7 tools · Single/Team: 17 · Team: all 28) — see [pricing](https://route6.me/pricing).

## How it works

The plugin is a thin proxy, not a reimplementation. At startup it asks the Route6 MCP gateway (`gw.route6.me/mcp`) for the current tool list and registers each tool with the server-provided schema; calls are forwarded over MCP (streamable HTTP, stdlib-only — no extra Python dependencies). New Route6 tools appear automatically without a plugin update. If the gateway is unreachable at startup, a bundled snapshot of the tool list is registered instead and calls still go live.

A usage skill ships with the plugin — load it in a session with:

```
skill_view("route6:route6")
```

It teaches the agent the common recipes: expose a local port on a public URL, fetch from a rotating clean IP, set up team coordination, and more.

## Configuration

| Env var | Required | Default | Purpose |
|---------|----------|---------|---------|
| `ROUTE6_API_KEY` | yes | — | Your API key from [route6.me](https://route6.me) |
| `ROUTE6_GATEWAY_URL` | no | `https://gw.route6.me/mcp` | Gateway override |
| `ROUTE6_TOOL_TIMEOUT` | no | `120` | Per-call timeout (seconds) |

## Prefer plain MCP?

Hermes speaks MCP natively — if you'd rather not install a plugin, add this to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  route6:
    url: "https://gw.route6.me/mcp"
    headers:
      Authorization: "Bearer YOUR_ROUTE6_API_KEY"
```

The plugin adds on top of that: guided key setup at install time, the bundled `route6:route6` skill, and offline-tolerant startup.

## Links

- **Get an API key:** [route6.me](https://route6.me)
- **Docs:** [docs.route6.me](https://docs.route6.me)
- **Examples:** [github.com/route6me/examples](https://github.com/route6me/examples)
- **Clients:** [`@route6/agent` (npm)](https://www.npmjs.com/package/@route6/agent) · [`route6` (PyPI)](https://pypi.org/project/route6/)

## License

MIT © [Route6](https://route6.me) — the plugin is open source; the Route6 network service it connects to is a commercial product.
