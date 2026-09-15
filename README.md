# Route6 plugin for Hermes Agent

Give your [Hermes Agent](https://github.com/NousResearch/hermes-agent) its own place on the internet: a real public **IPv6 address** inside your organisation's `/64`, a `*.on.route6.me` **hostname**, inbound **port forwarding** with a webhook URL, outbound **web fetch / search / browse / scrape** from its own address, and a **private mesh** with your other agents plus coordination tools (chat, whiteboard, task queue, roles).

Powered by [Route6](https://route6.me) — the network layer for AI agents. Every tool is on every plan, including Free (no card).

## Install

```bash
hermes plugins install route6me/hermes-plugin
```

The CLI installer prompts for your `ROUTE6_API_KEY` — create a free account at **[route6.me](https://route6.me)** and copy the key from the dashboard. Then enable the plugin when prompted (or `hermes plugins enable route6`).

That's it. All Route6 tools appear in your agent's tool list on next startup.

> **Installed from the Hermes GUI instead?** The GUI install doesn't prompt for the key, and its Keys page has no "add" button for plugin keys — add the key to Hermes' env file yourself, then restart (or Plugins → Rescan):
>
> ```bash
> echo 'ROUTE6_API_KEY=your_key_here' >> ~/.hermes/.env
> ```
>
> Once it's in the file, it shows up in the GUI Keys page and the plugin loads. (Don't use `hermes auth` — that's for model providers only.) Verify with `hermes plugins list` and `hermes tools`.

### Receiving traffic: run the Route6 client too

The plugin makes tool calls through the Route6 gateway, which is enough for everything outbound. To **receive** — port forwards, webhook URLs, the private mesh — the machine that runs the service also needs the Route6 client, kept up under systemd:

```bash
curl -fsSL https://dl.route6.me/install.sh | sudo sh -s -- --key sk_a6_your_key
sudo systemctl enable --now r6me
```

## What your agent can do with it

| | Tools |
|--|--|
| **Identity** | `identity` (get / set_ipv6 / check_reputation), `hostname_register` |
| **Network** | `net` (ping / traceroute / dns_resolve) |
| **Web** | `route6_web_fetch` (any URL from your own address; optional JS render + screenshots), `route6_web_search`, `route6_web_browse`, `route6_scrape` |
| **Inbound** | `port_forward` (create / list / delete, with `webhook: true` for a port-less HTTPS URL), `port_forward_secure`, `port_forward_tls` |
| **Mail** | `smtp_allowlist` |
| **Team mesh** | `team_status`, `team_ping`, `team_chat`, `team_whiteboard`, `team_task`, `team_capability`, `team_events`, `team_metrics`, `team_loop`, `team_project_task`, `team_roles` |
| **Account** | `plan_upgrade` |

The four web tools are registered with a `route6_` prefix so they never collide with Hermes' built-ins of the same name. Plans differ in capacity (agents, egress, scraper credits); a few capabilities need a paid plan — your own hostname, scraper top-ups, the Static IPv4 add-on, outbound SMTP — and the tool says so when called. See [pricing](https://route6.me/pricing).

## How it works

The plugin is a thin proxy, not a reimplementation. At startup it asks the Route6 MCP gateway (`gw.route6.me/mcp`) for the current tool list and registers each tool with the server-provided schema; calls are forwarded over MCP (streamable HTTP, stdlib-only — no extra Python dependencies). New Route6 tools appear automatically without a plugin update. If the gateway is unreachable at startup, a bundled snapshot of the tool list is registered instead and calls still go live.

A usage skill ships with the plugin — load it in a session with:

```
skill_view("route6:route6")
```

It teaches the agent the common recipes: a webhook URL restricted to its sender, fetching from its own address and rotating it, reaching teammates over the mesh, and team coordination.

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
- **Client:** [dl.route6.me](https://dl.route6.me/) · also [`@route6/agent` (npm)](https://www.npmjs.com/package/@route6/agent) and [`route6` (PyPI)](https://pypi.org/project/route6/)

## License

MIT © [Route6](https://route6.me) — the plugin is open source; the Route6 network service it connects to is a commercial product.
