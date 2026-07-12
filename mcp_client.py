"""Minimal MCP client for the Route6 gateway (streamable HTTP).

Stdlib-only on purpose — a Hermes plugin can't assume any third-party
package is installed. Speaks just enough of the MCP streamable-HTTP
transport for this plugin: initialize handshake (captures the
``mcp-session-id`` header), ``notifications/initialized``, ``tools/list``
and ``tools/call``. Responses may arrive as plain JSON or as an SSE
stream (``event: message`` / ``data: {...}``); both are handled.

The session is created lazily on first use and re-created once,
transparently, if the gateway reports it expired.
"""

from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request

DEFAULT_GATEWAY_URL = "https://gw.route6.me/mcp"
PROTOCOL_VERSION = "2025-03-26"

# tools/call must outlive the slowest tools: web_browse/scrape render
# pages, team_loop long-polls ~45s per hold.
CALL_TIMEOUT = int(os.environ.get("ROUTE6_TOOL_TIMEOUT", "120"))
SETUP_TIMEOUT = 10


class Route6MCPError(Exception):
    pass


class Route6MCP:
    def __init__(self, api_key: str, url: str | None = None):
        self._url = url or os.environ.get("ROUTE6_GATEWAY_URL") or DEFAULT_GATEWAY_URL
        self._api_key = api_key
        self._session_id: str | None = None
        self._lock = threading.Lock()
        self._id = 0

    # -- public API ---------------------------------------------------------

    def tools_list(self) -> list[dict]:
        result = self._request("tools/list", {}, timeout=SETUP_TIMEOUT)
        return result.get("tools", [])

    def tools_call(self, name: str, arguments: dict) -> str:
        """Call a tool; return its text content (Route6 tools emit JSON text).

        MCP-level errors come back as a JSON string with an ``error`` key so
        the caller (a Hermes tool handler) can return them verbatim.
        """
        result = self._request(
            "tools/call", {"name": name, "arguments": arguments or {}},
            timeout=CALL_TIMEOUT,
        )
        parts = [
            c.get("text", "")
            for c in result.get("content", [])
            if c.get("type") == "text"
        ]
        text = "\n".join(p for p in parts if p) or "{}"
        if result.get("isError"):
            try:
                json.loads(text)
                return text  # already a JSON error payload
            except (ValueError, TypeError):
                return json.dumps({"error": text})
        return text

    # -- wire ---------------------------------------------------------------

    def _request(self, method: str, params: dict, timeout: int) -> dict:
        self._ensure_session(timeout)
        try:
            msg = self._post(method, params, timeout)
        except Route6MCPError as e:
            # One transparent retry on session loss (gateway restart/expiry).
            if "session" not in str(e).lower():
                raise
            with self._lock:
                self._session_id = None
            self._ensure_session(timeout)
            msg = self._post(method, params, timeout)
        if "error" in msg:
            err = msg["error"]
            raise Route6MCPError(f"{err.get('message', 'MCP error')} (code {err.get('code')})")
        return msg.get("result", {})

    def _ensure_session(self, timeout: int) -> None:
        with self._lock:
            if self._session_id:
                return
            body, headers = self._raw_post(
                {
                    "jsonrpc": "2.0",
                    "id": self._next_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {},
                        "clientInfo": {"name": "hermes-route6-plugin", "version": "0.1.0"},
                    },
                },
                timeout=SETUP_TIMEOUT,
            )
            msg = self._parse_message(body, headers)
            if "error" in msg:
                raise Route6MCPError(f"initialize failed: {msg['error'].get('message')}")
            self._session_id = headers.get("mcp-session-id")
            if not self._session_id:
                raise Route6MCPError("gateway did not return an mcp-session-id")
            self._raw_post(
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                timeout=SETUP_TIMEOUT,
                expect_body=False,
            )

    def _post(self, method: str, params: dict, timeout: int) -> dict:
        body, headers = self._raw_post(
            {"jsonrpc": "2.0", "id": self._next_id(), "method": method, "params": params},
            timeout=timeout,
        )
        return self._parse_message(body, headers)

    def _raw_post(self, payload: dict, timeout: int, expect_body: bool = True):
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        req = urllib.request.Request(
            self._url, data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace"), {
                    k.lower(): v for k, v in resp.headers.items()
                }
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            if e.code == 401:
                raise Route6MCPError(
                    "Route6 rejected the API key (401). Check ROUTE6_API_KEY — "
                    "get a key at https://route6.me"
                ) from None
            raise Route6MCPError(f"gateway HTTP {e.code}: {detail}") from None
        except urllib.error.URLError as e:
            raise Route6MCPError(f"cannot reach Route6 gateway {self._url}: {e.reason}") from None

    @staticmethod
    def _parse_message(body: str, headers: dict) -> dict:
        ctype = headers.get("content-type", "")
        if "text/event-stream" in ctype:
            last = None
            for line in body.splitlines():
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data:
                        try:
                            last = json.loads(data)
                        except ValueError:
                            continue
            if last is None:
                raise Route6MCPError("empty SSE response from gateway")
            return last
        if not body.strip():
            return {}
        try:
            return json.loads(body)
        except ValueError:
            raise Route6MCPError(f"non-JSON response from gateway: {body[:200]}") from None

    def _next_id(self) -> int:
        self._id += 1
        return self._id
