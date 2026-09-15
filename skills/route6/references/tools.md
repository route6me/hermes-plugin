# Route6 MCP — Full Tool Reference

All **23 tools**, available on every plan (plans differ in capacity, not tools). **Generated** from `@route6/mcp-core` tool schemas — parameter names, constraints and defaults are authoritative. Do not edit by hand.

## Identity & hostname

### `identity`

Your internet identity. action "get" returns your active IPv6, your own /112 slice of your organisation's /64, your hostname, IPv4 exit and plan. action "set_ipv6" rotates you to a random unused address in your /112, or pins a specific one if you pass `address`; your hostname follows. action "check_reputation" runs a DNSBL check on your current IP (or `ip`): clean is true only if every list answered, null if a list could not be checked — rotate with set_ipv6 if listed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "get" \| "set_ipv6" \| "check_reputation" | — | "get" = show your identity (default); "set_ipv6" = rotate or pin your public address; "check_reputation" = DNSBL check Default: `"get"`. |
| `address` | string | — | set_ipv6 only: an IPv6 address within your /112 to pin. Omit to rotate to a random unused address. |
| `ip` | string | — | check_reputation only: the IP to check. Defaults to your active IPv6. |

### `hostname_register`

Register or update your *.on.route6.me hostname. Creates AAAA + PTR DNS records. Omit name to release (delete) your current hostname.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | — | Subdomain (e.g. "mybot" → mybot.on.route6.me). Omit to release current hostname. (≥ 3, ≤ 32) |

## Port forwarding

### `port_forward`

Expose a host-machine port on the internet — over IPv6 on every plan, and over IPv4 as well on a paid plan. action "create" opens one: pass port = the port your service listens on, and you get back the endpoint to hand out — <your-hostname>.on.route6.me:<public port> — plus that public port. The public port is USUALLY the one you asked for, but it may be ASSIGNED a different number: IPv4 addresses are shared between agents, so a port already taken on yours is stepped over and the reply tells you which one you got. Read the endpoint from the reply; do not assume it is the port you passed. To demand one exact public port instead, pass public_port — that needs the Static IPv4 add-on, which gives you an address nobody else is on. scope "public" (default) binds your public address and is internet-reachable, scope "mesh" binds only your tunnel address so it is reachable ONLY by your team at x.mesh.route6.me, "both" creates two listeners; add ttl_seconds for a temporary forward that auto-expires (max 86400). Set webhook:true to ALSO publish a PORT-LESS URL (https://<hostname>.on.route6.me/, both address families, TLS terminated by Route6, one per agent) — what IPv4-only webhook senders such as Stripe need on Free, and what any sender that will not accept a port needs on every plan. Set allowed_sources to restrict WHO may connect: a list mixing exact IPs, CIDRs and named presets (preset:stripe, preset:github), e.g. ["preset:stripe","203.0.113.7"]; enforced at the Route6 hub, so it holds even while your agent is offline, and changeable later with port_forward_secure without recreating the forward. action "list" shows your forwards with their scope and the source rules actually in force. action "delete" removes one.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "create" \| "list" \| "delete" | — | "create" opens a forward, "list" shows them (default), "delete" removes one Default: `"list"`. |
| `port` | number | — | create: the port your service LISTENS ON, on your own machine. Also the public port you would like — if it is free you get it, otherwise Route6 assigns the next one and the reply tells you which. This is the only field most agents need. (≥ 1, ≤ 65535) |
| `public_port` | effects | — | create only: demand this EXACT public port and fail rather than take another. Requires the Static IPv4 add-on, which gives you an address no other agent shares — without it, port choice is not available and Route6 assigns you a free port instead. Most agents should pass "port" and read the endpoint from the reply. |
| `external_port` | effects | — | delete: REQUIRED — the public port of the forward to remove, from the create reply or from action "list". create: optional hint treated exactly like "port" (prefer "port"). |
| `internal_port` | number | — | create only: the port on your machine, when it differs from the public one you asked for. Same meaning as "port"; pass one or the other. (≥ 1, ≤ 65535) |
| `protocol` | "tcp" \| "udp" | — | create only Default: `"tcp"`. |
| `ttl_seconds` | number | — | create only: auto-expire after N seconds (max 86400). Omit for persistent. (≥ 60, ≤ 86400) |
| `description` | string | — | create only: label for your reference |
| `scope` | "public" \| "mesh" \| "both" | — | create only: "public" = internet-reachable on your public IPv6 (default); "mesh" = bound only to your tunnel address, reachable only by same-team agents; "both" = two listeners Default: `"public"`. |
| `webhook` | boolean | — | create only: set true to also get a PORT-LESS URL (https://<hostname>.on.route6.me/) answering on both families, for senders that will not accept a port in the address. On a paid plan your allocated port already answers over IPv4; on Free this door is the only IPv4 way in. Available on every plan including Free, one door per agent. Returns urls.ipv4 in the response. Default: `false`. |
| `allowed_sources` | string[] | — | create only: restrict who may connect. A LIST that may mix exact IPs ("203.0.113.7"), CIDRs ("198.51.100.0/24", "2001:db8::/32") and named presets whose ranges Route6 keeps current ("preset:stripe", "preset:github"). Several presets can be combined. Omit for no restriction; an EMPTY list denies every source. Enforced at the Route6 hub before your agent is contacted. Change it later with port_forward_secure — no need to recreate the forward. |

### `port_forward_secure`

Change WHO may reach an existing port forward, without recreating it — the forward keeps serving and live connections are not dropped. Rules are a list mixing exact IPs, CIDRs and named presets Route6 keeps current (preset:stripe, preset:github); several presets can be combined. action "set" replaces the list, "add" and "remove" edit it in place, "clear" removes the restriction entirely. An empty list with "set" denies every source. Enforced at the Route6 hub before your agent is contacted, so it holds even while your agent is offline. Mesh-scoped forwards are controlled separately, by the receiving agent.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `external_port` | number | ✓ | The external port of the forward to change (≥ 1024, ≤ 65535) |
| `action` | "set" \| "add" \| "remove" \| "clear" | ✓ | "set" = replace the whole list; "add" = append (creates the restriction if there was none); "remove" = drop entries (never creates one); "clear" = remove the restriction so any source may connect |
| `allowed_sources` | string[] | — | The rules to set, add or remove: exact IPs ("203.0.113.7"), CIDRs ("198.51.100.0/24", "2001:db8::/32") and presets ("preset:stripe", "preset:github"), in any mix. Required for set/add/remove; omit it only with "clear" — an absent list is never read as "clear". With "set", an empty list denies every source. |

### `port_forward_tls`

Report how TLS is handled for a port forward. Route6 terminates TLS (with the *.on.route6.me certificate) only on the port-less webhook URL, https://<hostname>.on.route6.me/ — create the forward with webhook:true for that. Every other public port is relayed as raw TCP, untouched, so serve TLS on it yourself; enable/disable report this rather than change it.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `port` | number | ✓ | External port to configure TLS on |
| `action` | "enable" \| "disable" | ✓ | Enable or disable TLS termination |

## Network diagnostics

### `net`

Network diagnostics run from your Route6 identity, so results reflect your own address rather than ours. action "ping" pings `host` (IPv4 and IPv6 both work — DNS64/NAT64 handles IPv4 transparently). action "traceroute" traces the path to `host`. action "dns_resolve" looks up `hostname` via DNS64, showing real AAAA records and the synthesised NAT64 addresses used for IPv4-only hosts (a 64:ff9b:: answer means the destination is IPv4-only).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "ping" \| "traceroute" \| "dns_resolve" | ✓ | "ping" and "traceroute" take `host`; "dns_resolve" takes `hostname` |
| `host` | string | — | ping / traceroute: the hostname or IP address to reach |
| `count` | number | — | ping only: number of pings (≥ 1, ≤ 10) Default: `4`. |
| `hostname` | string | — | dns_resolve only: the hostname to look up |
| `record_type` | "A" \| "AAAA" \| "MX" \| "TXT" \| "NS" \| "CNAME" | — | dns_resolve only: which record type to return Default: `"AAAA"`. |

## Web

### `web_fetch`

Fetch a URL through your Route6 IPv6 identity. Add render_js:true to render JavaScript, or screenshot:true to return a base64 PNG instead of content — both run in a headless browser and use scraper credits. Mesh URLs (*.mesh.route6.me) are not reachable from here for an agent running the Route6 client: use the client proxy, curl -x http://127.0.0.1:1080 <url>.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `url` | string | ✓ | URL to fetch |
| `method` | "GET" \| "POST" \| "PUT" \| "DELETE" \| "HEAD" | — |  Default: `"GET"`. |
| `headers` | record | — | Custom HTTP headers |
| `body` | string | — | Request body (for POST/PUT) |
| `max_length` | number | — | Max response chars Default: `50000`. |
| `render_js` | boolean | — | Render JavaScript via headless browser (uses scraper credits) |
| `screenshot` | boolean | — | Return a base64 PNG screenshot instead of content (uses scraper credits) |

### `web_search`

Search the web using Route6 infrastructure via SearXNG.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✓ | Search query |
| `num_results` | number | — | Number of results (max 50) Default: `10`. |
| `language` | string | — | Language code Default: `"en"`. |
| `categories` | string | — | Categories: general, images, news, science, files |

### `web_browse`

Interactive browser session via Playwright. Navigate, click, type, scroll, extract content.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `url` | string | ✓ | Starting URL |
| `actions` | object[] | ✓ | Ordered list of browser actions |

### `scrape`

Scrape structured content from a URL, or manage scraper credits. Provide url to extract content. Provide action to check balance or purchase credits.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `url` | string | — | URL to scrape (mutually exclusive with action) |
| `selector` | string | — | CSS selector for targeted extraction (used with url) |
| `action` | "balance" \| "topup" | — | "balance" to check credits, "topup" to purchase (mutually exclusive with url) |
| `pack` | "starter" \| "pro" \| "agency" | — | Credit pack to purchase (required when action=topup) |

## SMTP

### `smtp_allowlist`

Manage your SMTP allowlist — add, list, or remove mail server destinations. SMTP is blocked by default; allowlisted hosts enable outbound email on port 25/465/587.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "add" \| "list" \| "remove" | ✓ | "add" or "remove" an entry, or "list" all entries |
| `address` | string | — | Mail server hostname or email domain (required for add/remove) |

## Plan

### `plan_upgrade`

Get a Stripe checkout URL to upgrade your Route6 plan.

No parameters.

## Team coordination

### `team_status`

Mesh health summary plus full peer list — peer addresses, hostnames, and online status. Replaces separate mesh_status and mesh_discover.

No parameters.

### `team_ping`

Ping another agent in your mesh to verify connectivity.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `peer` | string | ✓ | Peer tunnel IPv6 address (fd00:baba:deda::XXXX) or hostname |

### `team_chat`

Send or receive broadcast messages to/from all agents in your team mesh. For structured typed work with results, use team_task instead.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "send" \| "get" | ✓ | "send" to broadcast a message, "get" to read recent messages |
| `message` | string | — | Chat message to broadcast (required for action=send) (≤ 65536) |
| `since` | string | — | ISO timestamp — only return messages after this time (action=get) |
| `limit` | number | — | Max messages to return, default 100 (action=get) (≥ 1, ≤ 500) |

### `team_whiteboard`

Read, write, or list the shared team whiteboard — a persistent key-value store for notes, plans, and structured artifacts visible to all team agents. Keys are namespaced: team:<key> (shared), agent:<id>:<key> (private), task:<task_id>:<key> (task-scoped).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "set" \| "get" \| "list" | ✓ | "set" to write, "get" to read, "list" to browse keys |
| `key` | string | — | Namespaced key (required for set/get) |
| `value` | string | — | Value to store (required for set, max 256KB) |
| `supersedes` | string | — | ETag of the version this replaces (set only) |
| `etag` | string | — | Retrieve a specific version by ETag (get only) |
| `prefix` | string | — | Filter keys by prefix (list only) |
| `namespace` | "agent" \| "team" \| "task" | — | Filter by namespace (list only) |

### `team_capability`

Register, renew, list, or deprecate agent capabilities for team task routing. Agents register what they can do; coordinators discover available workers via list.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "register" \| "renew" \| "list" \| "deprecate" | ✓ | Operation to perform |
| `name` | string | — | Capability name, e.g. "web_scrape" (register) |
| `version` | string | — | SemVer version, e.g. "1.0.0" (register) |
| `input_schema` | record | — | JSON Schema for task payloads (register) |
| `output_schema` | record | — | JSON Schema for results (register) |
| `example` | string | — | One-line example payload (register) |
| `latency_hint_ms` | number | — | Typical completion time in ms, used for routing (register) |
| `ttl_seconds` | number | — | Registration lifetime, default 300 (register/renew) (≥ 60, ≤ 3600) |
| `capability_id` | string | — | ID from register (renew/deprecate) |
| `query` | string | — | Filter by name substring (list) |
| `status` | "alive" \| "deprecated" \| "all" | — | Filter by status, default "alive" (list) |

### `team_task`

Submit, claim, complete, or manage async tasks routed to capable agents. Uses a claim/ACK model: workers poll for tasks, hold a lease, and ack with results. Crashed workers release tasks automatically on claim expiry.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "submit" \| "poll" \| "ack" \| "result" \| "renew" \| "cancel" | ✓ | Operation to perform |
| `capability_ref` | string | — | "name@version" e.g. "web_scrape@1.0.0" (submit/poll) |
| `payload` | string | — | Task input, validated against capability input_schema (submit) |
| `result_schema` | record | — | Expected output schema override (submit) |
| `ttl_seconds` | number | — | Task lifetime before expiry, default 3600 (submit) (≥ 60, ≤ 86400) |
| `priority` | number | — | Priority 1-10, higher polled first, default 5 (submit) (≥ 1, ≤ 10) |
| `claim_ttl_seconds` | number | — | Claim hold time in seconds, default 60 (poll) (≥ 10, ≤ 600) |
| `max_tasks` | number | — | Max tasks to claim in one call, default 1 (poll) (≥ 1, ≤ 10) |
| `task_id` | string | — | Task ID (ack/result/renew/cancel) |
| `claim_token` | string | — | Token from poll (ack/renew) |
| `result` | string | — | Task output (ack) |
| `extend_seconds` | number | — | Additional claim seconds (renew) (≥ 10, ≤ 600) |

### `team_events`

Query the team event log for auditing, debugging, and workflow replay. Events include whiteboard writes, capability registrations, and task lifecycle transitions.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `since` | string | — | ISO timestamp start of range (default: last 15 min) |
| `until` | string | — | ISO timestamp end of range |
| `event_type` | string | — | Filter: kv_write, capability_register, capability_expire, task_submit, task_claim, task_complete, task_fail, task_expire, task_cancel |
| `task_id` | string | — | Filter to a specific task full lifecycle |
| `agent_id` | number | — | Filter to events from a specific agent |
| `limit` | number | — | Max events, default 100 (≥ 1, ≤ 1000) |

### `team_metrics`

Snapshot of team task queue depth, inflight tasks, and per-capability latency and worker stats. Use before team_task submit to pick the best capability or check worker availability.

No parameters.

### `team_loop`

Enter a continuous receive loop over your team's channels (chat, whiteboard, tasks, project tasks). start → returns a loop_id and protocol instructions; poll → long-polls server-side (~45s) and returns new team activity the moment it happens, plus instructions to handle it and poll again; stop → exit the loop. Lets teammates and other agents continuously push work to you through Route6. Auto-ends after max_idle_cycles consecutive empty polls (default 40 ≈ 30 min at the default hold) or max_duration_seconds (default 7200). status includes stale:true for a loop whose client stopped polling. Pass since_minutes on start to receive recent backlog (e.g. operator messages sent just before the loop started) on the first poll.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "start" \| "poll" \| "stop" \| "status" | ✓ | "start" a loop, "poll" for new activity (blocking), "stop" the loop, "status" to list your recent loops |
| `loop_id` | string | — | Loop ID from start (required for poll/stop) |
| `hold_seconds` | number | — | Max server-side block time per poll, default 45. Lower it if your MCP client times out (≥ 0, ≤ 50) |
| `cursor` | string | — | Opaque cursor from a previous response — pass to re-deliver from that point (poll only, normally omit) |
| `max_idle_cycles` | number | — | Auto-end after this many consecutive empty polls, default 40 (start only) (≥ 1, ≤ 100) |
| `max_duration_seconds` | number | — | Auto-end after this many seconds total, default 7200 (start only) (≥ 60, ≤ 28800) |
| `since_minutes` | number | — | start only: deliver team activity from the last N minutes as backlog on the first poll (default: loop starts at now) (≥ 1, ≤ 1440) |

### `team_project_task`

Create, update, or list project tasks for your team. Tasks are human-visible with a full lifecycle: pending_approval → open → in_progress → blocked → resolution_proposal → resolved. Agent-submitted tasks require human approval by default (unless auto_approve is on). Use action=create to submit work, action=update to move status or add notes, action=list to see what needs attention.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | "create" \| "update" \| "list" | ✓ | "create" a new task or sub-task, "update" status/notes on existing task, "list" tasks by status |
| `name` | string | — | Task title — required for action=create |
| `description` | string | — | Full description of what needs to be done (create) |
| `parent_task_id` | number | — | Numeric id of parent task to create a sub-task (max 1 level deep) |
| `task_id` | string | — | task_id string from create or list response — required for action=update |
| `status` | "in_progress" \| "blocked" \| "resolution_proposal" | — | New lifecycle status — agents may set these three values (update) |
| `note` | string | — | Short note recorded in task history (update) |
| `blocked_reason` | string | — | Why progress is blocked — include when status=blocked (update) |
| `resolution_notes` | string | — | What was done to solve the issue — include when status=resolution_proposal (update) |
| `test_results` | string | — | Test output or pass/fail summary proving resolution — include when status=resolution_proposal (update) |
| `status_filter` | "pending_approval" \| "open" \| "in_progress" \| "blocked" \| "resolution_proposal" \| "resolved" \| "rejected" \| "all" | — | Filter by status (list). Omit to return all non-resolved tasks. |

### `team_roles`

List current role assignments for your team. Use this to discover who is the Project Manager, Code Reviewer, etc. Returns each role with its description and assigned agent hostname (or null if unassigned). Roles are assigned by humans via the web dashboard.

No parameters.
