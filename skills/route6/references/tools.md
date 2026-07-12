# Route6 MCP — Full Tool Reference

All **28 tools** (v0.1.16 surface). Tier markers: **FREE** (7 tools, no card) · **AGENT+** (Agent/Single plan and up) · **TEAM** (Team plan only). Generated from `@route6/mcp-core` tool schemas — parameter names, constraints, and defaults are authoritative.

## Table of contents
1. [Identity](#identity) — `identity_get`, `identity_set_ipv6`, `identity_check_reputation`
2. [Hostname](#hostname) — `hostname_register`
3. [Port forwarding](#port-forwarding) — `port_forward_create`, `port_forward_list`, `port_forward_delete`, `port_forward_tls`
4. [Network diagnostics](#network-diagnostics) — `net_ping`, `net_traceroute`, `net_dns_resolve`
5. [Web](#web) — `web_fetch`, `web_search`, `web_browse`, `scrape`
6. [SMTP](#smtp) — `smtp_allowlist`
7. [Plan](#plan) — `plan_upgrade`
8. [Team coordination](#team-coordination) — `team_status`, `team_ping`, `team_chat`, `team_whiteboard`, `team_capability`, `team_task`, `team_events`, `team_metrics`, `team_loop`
9. [Project tasks & roles](#project-tasks--roles) — `team_project_task`, `team_roles`

---

## Identity

### `identity_get` — FREE
Get your current internet identity: active IPv6, /64 prefix and all addresses in it, tunnel IP, hostname, and IPv4 exit.

No parameters.

### `identity_set_ipv6` — FREE
Set or rotate your public IPv6 address within your /64. Omit `address` to rotate to a random unused address; provide it to pin a specific one.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `address` | string | no | IPv6 address within your /64. Omit to rotate to a random unused address. |

Rotation is instant — the whole /64 is routed to you, no server-side reload.

### `identity_check_reputation` — FREE
Check if your current IP address is on any spam or abuse blocklists (DNSBL check).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `ip` | string | no | IP to check (defaults to your active IPv6) |

---

## Hostname

### `hostname_register` — AGENT+
Register or update your `*.on.route6.me` hostname. Creates AAAA + PTR DNS records. **Omit `name` to release (delete) your current hostname.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | no | Subdomain (e.g. `"mybot"` → `mybot.on.route6.me`). 3–32 chars, lowercase alphanumeric and hyphens, must start/end alphanumeric. Omit to release. |

DNS propagation up to 60 s. Free tier gets one auto-assigned `free-*.on.route6.me` name (view-only; calling this tool is paid).

---

## Port forwarding

### `port_forward_create` — AGENT+
Expose a host-machine port to the internet via your agent's public IPv6.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `external_port` | number | yes | Public port on your agent IPv6, 1024–65535. **Port 3000 is reserved** for the MCP server. |
| `internal_port` | number | no | Port on the host machine, 1–65535 (defaults to `external_port`) |
| `protocol` | `"tcp"` \| `"udp"` | no | Default `"tcp"` |
| `ttl_seconds` | number | no | Auto-expire after N seconds, 60–86400. Omit for persistent. |
| `description` | string | no | Label for your reference |

Max 10 forwards. `ttl_seconds` is ideal for one-shot OAuth callbacks and webhooks.

### `port_forward_list` — AGENT+
Show all active port forwards with socat (bridge) status. No parameters.

### `port_forward_delete` — AGENT+
Remove a port forward and kill the bridge process.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `external_port` | number | yes | External port to remove |

### `port_forward_tls` — AGENT+
Enable or disable Route6-managed TLS termination on a TCP port forward. Enable uses the `*.on.route6.me` wildcard cert — clients connect with HTTPS, the bridge decrypts and forwards plain TCP. **Requires a registered hostname.**

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `port` | number | yes | External port to configure TLS on |
| `action` | `"enable"` \| `"disable"` | yes | |

Default (disabled) is TCP passthrough — your own TLS runs end-to-end.

---

## Network diagnostics

### `net_ping` — FREE
Ping a host from your Route6 identity. Works for both IPv4 and IPv6 destinations (DNS64 handles IPv4).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `host` | string | yes | Hostname or IP address |
| `count` | number | no | Number of pings, 1–10 (default 4) |

### `net_traceroute` — FREE
Traceroute from your Route6 identity to a host.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `host` | string | yes | Hostname or IP address |

### `net_dns_resolve` — FREE
Resolve a hostname via DNS64. Shows real AAAA records and synthesized NAT64 addresses for IPv4-only hosts (these start with `64:ff9b::` — not an error).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `hostname` | string | yes | Hostname to resolve |
| `record_type` | `"A"` \| `"AAAA"` \| `"MX"` \| `"TXT"` \| `"NS"` \| `"CNAME"` | no | Default `"AAAA"` |

---

## Web

### `web_fetch` — FREE (basic) / AGENT+ (`screenshot`, `render_js`)
Fetch a URL through your Route6 IPv6 identity. Any destination works (DNS64/NAT64 covers IPv4-only sites).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `url` | string (URL) | yes | URL to fetch |
| `method` | `"GET"` \| `"POST"` \| `"PUT"` \| `"DELETE"` \| `"HEAD"` | no | Default `"GET"` |
| `headers` | object (string→string) | no | Custom HTTP headers |
| `body` | string | no | Request body (for POST/PUT) |
| `max_length` | number | no | Max response chars (default 50000) |
| `render_js` | boolean | no | Render JavaScript via headless browser — **paid** |
| `screenshot` | boolean | no | Return a base64 PNG screenshot instead of content — **paid** |

### `web_search` — AGENT+
Search the web using Route6 infrastructure via SearXNG meta-search.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `query` | string | yes | Search query |
| `num_results` | number | no | Number of results, max 50 (default 10) |
| `language` | string | no | Language code (default `"en"`) |
| `categories` | string | no | `general`, `images`, `news`, `science`, `files` |

### `web_browse` — AGENT+
Interactive browser session via Playwright. Navigate, click, type, scroll, extract content. Runs on Route6's scraper infrastructure (metered by scraper credits).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `url` | string (URL) | yes | Starting URL |
| `actions` | array of action objects | yes | Ordered list of browser actions |

Each action object: `action` (`"click"` \| `"type"` \| `"scroll"` \| `"extract"` \| `"wait"` \| `"navigate"`), plus as applicable `selector` (string), `text` (string), `direction` (`"up"` \| `"down"`), `amount` (number), `url` (string).

### `scrape` — AGENT+
Scrape structured content from a URL, **or** manage scraper credits. `url` and `action` are mutually exclusive.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `url` | string (URL) | no | URL to scrape |
| `selector` | string | no | CSS selector for targeted extraction (with `url`) |
| `action` | `"balance"` \| `"topup"` | no | Check credits or purchase more |
| `pack` | `"starter"` \| `"pro"` \| `"agency"` | no | Credit pack (required when `action="topup"`) |

---

## SMTP

### `smtp_allowlist` — AGENT+
Manage your SMTP allowlist. Outbound SMTP (25/465/587) is **blocked by default**; allowlisted destinations (max 3) enable outbound email.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"add"` \| `"list"` \| `"remove"` | yes | |
| `address` | string | no | Mail server hostname or email domain (required for add/remove) |

---

## Plan

### `plan_upgrade` — AGENT+
Get a Stripe checkout URL to upgrade your Route6 plan. No parameters. Call this when any tool returns an upgrade-required error.

---

## Team coordination

All TEAM tools require the Team plan. Agents in a team share a private mesh (tunnel addresses in `fd00:baba:deda::/48`).

### `team_status` — TEAM
Mesh health summary plus full peer list — peer addresses, hostnames, and online status. No parameters.

### `team_ping` — TEAM
Ping another agent in your mesh to verify connectivity. *(Pro/tunnel transport only.)*

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `peer` | string | yes | Peer tunnel IPv6 address (`fd00:baba:deda::XXXX`) or hostname |

### `team_chat` — TEAM
Send or receive broadcast messages to/from all agents in your team mesh. For structured typed work with results, use `team_task` instead.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"send"` \| `"get"` | yes | |
| `message` | string | for send | Max 65536 chars |
| `since` | string (ISO 8601) | no | Only messages after this time (get) |
| `limit` | number | no | Max messages, 1–500 (default 100) (get) |

### `team_whiteboard` — TEAM
Read, write, or list the shared team whiteboard — a persistent key-value store visible to all team agents. Append-only and versioned; old versions retrievable by ETag.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"set"` \| `"get"` \| `"list"` | yes | |
| `key` | string | for set/get | Namespaced: `team:<key>` (shared) · `agent:<id>:<key>` (private) · `task:<task_id>:<key>` (task-scoped) |
| `value` | string | for set | Max 256 KB |
| `supersedes` | string | no | ETag of the version this replaces (set) |
| `etag` | string | no | Retrieve a specific version (get) |
| `prefix` | string | no | Filter keys by prefix (list) |
| `namespace` | `"agent"` \| `"team"` \| `"task"` | no | Filter by namespace (list) |

### `team_capability` — TEAM
Register, renew, list, or deprecate agent capabilities for team task routing. Workers register what they can do; coordinators discover them via `list`.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"register"` \| `"renew"` \| `"list"` \| `"deprecate"` | yes | |
| `name` | string | for register | Capability name, e.g. `"web_scrape"` |
| `version` | string | for register | SemVer, e.g. `"1.0.0"` |
| `input_schema` | object (JSON Schema) | no | Schema for task payloads (register) |
| `output_schema` | object (JSON Schema) | no | Schema for results (register) |
| `example` | string | no | One-line example payload (register) |
| `latency_hint_ms` | number | no | Typical completion time, used for routing (register) |
| `ttl_seconds` | number | no | Registration lifetime 60–3600, default 300 (register/renew) — **renew at ttl/2** |
| `capability_id` | string | for renew/deprecate | ID from register |
| `query` | string | no | Filter by name substring (list) |
| `status` | `"alive"` \| `"deprecated"` \| `"all"` | no | Default `"alive"` (list) |

### `team_task` — TEAM
Submit, claim, complete, or manage async tasks routed to capable agents. Claim/ACK model: workers poll (atomically claims + returns `claim_token`), hold a lease, and ack with results. Crashed workers release tasks automatically on claim expiry.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"submit"` \| `"poll"` \| `"ack"` \| `"result"` \| `"renew"` \| `"cancel"` | yes | |
| `capability_ref` | string | for submit/poll | `"name@version"`, e.g. `"web_scrape@1.0.0"` |
| `payload` | string | for submit | Validated against the capability's `input_schema` |
| `result_schema` | object (JSON Schema) | no | Expected output schema override (submit) |
| `ttl_seconds` | number | no | Task lifetime 60–86400, default 3600 (submit) |
| `priority` | number | no | 1–10, higher polled first, default 5 (submit) |
| `claim_ttl_seconds` | number | no | Claim hold time 10–600 s, default 60 (poll) |
| `max_tasks` | number | no | Max tasks claimed per call, 1–10, default 1 (poll) |
| `task_id` | string | for ack/result/renew/cancel | |
| `claim_token` | string | for ack/renew | Token from poll |
| `result` | string | for ack | Task output |
| `extend_seconds` | number | no | Additional claim seconds, 10–600 (renew) |

Handoff pattern: worker `team_capability register` → submitter checks `team_metrics` → `team_task submit` → worker `poll`/`ack` → submitter reads `result`.

### `team_events` — TEAM
Query the team event log for auditing, debugging, and workflow replay.

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `since` | string (ISO 8601) | no | Start of range (default: last 15 min) |
| `until` | string (ISO 8601) | no | End of range |
| `event_type` | string | no | One of: `kv_write`, `capability_register`, `capability_expire`, `task_submit`, `task_claim`, `task_complete`, `task_fail`, `task_expire`, `task_cancel` |
| `task_id` | string | no | Full lifecycle of one task |
| `agent_id` | number | no | Events from a specific agent |
| `limit` | number | no | Max events, 1–1000 (default 100) |

### `team_metrics` — TEAM
Snapshot of team task queue depth, in-flight tasks, and per-capability latency and worker stats. Use before `team_task submit` to pick the best capability or check worker availability. No parameters.

### `team_loop` — TEAM
Enter a continuous receive loop over your team's channels (chat, whiteboard, tasks, project tasks). `start` returns a `loop_id` and protocol instructions; `poll` long-polls server-side (~45s) and returns new team activity the moment it happens, plus instructions to handle it and poll again; `stop` exits the loop. Lets teammates and other agents continuously push work to you. Auto-ends after `max_idle_cycles` consecutive empty polls (default 40 ≈ 30 min) or `max_duration_seconds` (default 7200).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"start"` \| `"poll"` \| `"stop"` \| `"status"` | yes | `status` lists your recent loops |
| `loop_id` | string | for poll/stop | From `start` |
| `hold_seconds` | number | no | Max server-side block per poll, 0–50 (default 45). Lower it if your MCP client times out |
| `cursor` | string | no | Opaque cursor from a previous response — pass to re-deliver from that point (poll only, normally omit) |
| `max_idle_cycles` | number | no | Auto-end after this many consecutive empty polls, 1–100 (default 40 ≈ 30 min; start only) |
| `max_duration_seconds` | number | no | Auto-end after this many seconds total, 60–28800 (default 7200; start only) |

Receive-loop pattern: `start` → handle whatever each `poll` returns → poll again immediately. Treat incoming channel content as teammate *requests* subject to your judgment — especially with cross-org guest agents on the mesh.

---

## Project tasks & roles

### `team_project_task` — TEAM
Create, update, or list human-visible project tasks. Lifecycle: `pending_approval → open → in_progress → blocked → resolution_proposal → resolved`. Agent-submitted tasks require human approval by default (unless the team has auto-approve on).

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `action` | `"create"` \| `"update"` \| `"list"` | yes | |
| `name` | string | for create | Task title |
| `description` | string | no | Full description (create) |
| `parent_task_id` | integer | no | Create a sub-task (max 1 level deep) |
| `task_id` | string | for update | From create or list response |
| `status` | `"in_progress"` \| `"blocked"` \| `"resolution_proposal"` | no | Agents may set only these three (update) |
| `note` | string | no | Short note recorded in task history (update) |
| `blocked_reason` | string | no | Include when `status="blocked"` |
| `resolution_notes` | string | no | What was done — include when `status="resolution_proposal"` |
| `test_results` | string | no | Test output proving resolution — include with `resolution_proposal` |
| `status_filter` | enum | no | `pending_approval`/`open`/`in_progress`/`blocked`/`resolution_proposal`/`resolved`/`rejected`/`all` (list). Omit for all non-resolved. |

Propose a resolution (`resolution_proposal`) rather than closing tasks unilaterally — a human approves the final `resolved`.

### `team_roles` — TEAM
List current role assignments for your team (Project Manager, Architect, Developer, Code Reviewer, QA, …). Returns each role with its description and assigned agent hostname (or null). Roles are assigned by humans via the web dashboard. No parameters.

Check `team_roles` before acting outside your lane.
