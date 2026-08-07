#!/usr/bin/env python3
"""
c9_browse_bridge.py â C9 â PinchTab Web Browse Bridge
======================================================
Wraps PinchTab's HTTP API (localhost:9867) and posts results to the C9 bus.
Designed for Termux/Android sovereign stack. Zero heavy deps.

Usage:
    python3 c9_browse_bridge.py nav https://arxiv.org/abs/2506.16544
    python3 c9_browse_bridge.py snap --filter interactive
    python3 c9_browse_bridge.py text
    python3 c9_browse_bridge.py click e5
    python3 c9_browse_bridge.py search "causal set theory cosmology"

AutoBaby integration:
    Add to AutoBaby's tool registry. When research needs live web data,
    AutoBaby calls this bridge instead of failing on "Connection refused".

PinchTab install (Termux):
    curl -fsSL https://pinchtab.com/install.sh | bash
    pinchtab daemon install
    pinchtab daemon

Author: C9 Assembly
"""

import json
import sys
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# ââ Configuration ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
PINCHTAB_HOST = os.environ.get("PINCHTAB_HOST", "127.0.0.1")
PINCHTAB_PORT = int(os.environ.get("PINCHTAB_PORT", "9867"))
PINCHTAB_URL = f"http://{PINCHTAB_HOST}:{PINCHTAB_PORT}"

C9_BUS_PATH = os.environ.get("C9_BUS_PATH", os.path.expanduser("~/cloud9/c9_bus.jsonl"))
C9_ENTITY = os.environ.get("C9_ENTITY", "c9_browse_bridge")

# Default profile/instance IDs (managed automatically)
_DEFAULT_PROFILE = None
_DEFAULT_INSTANCE = None
_DEFAULT_TAB = None

# ââ Low-level HTTP helpers âââââââââââââââââââââââââââââââââââââââââââââââââââ

def _http(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a JSON HTTP request to PinchTab."""
    url = f"{PINCHTAB_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"PinchTab HTTP {e.code}: {body}") from e
    except Exception as e:
        raise RuntimeError(f"PinchTab unreachable at {url}: {e}") from e


def _get(endpoint: str) -> Dict[str, Any]:
    return _http("GET", endpoint)


def _post(endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    return _http("POST", endpoint, data)


# ââ C9 Bus integration âââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def _bus_emit(entry_type: str, payload: Dict[str, Any]) -> None:
    """Append a structured event to the C9 bus JSONL."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entity": C9_ENTITY,
        "type": entry_type,
        "payload": payload,
    }
    line = json.dumps(event, ensure_ascii=False)
    try:
        with open(C9_BUS_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(C9_BUS_PATH), exist_ok=True)
        with open(C9_BUS_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[WARN] Bus emit failed: {e}", file=sys.stderr)


# ââ PinchTab lifecycle helpers âââââââââââââââââââââââââââââââââââââââââââââââââ

def ensure_profile(name: str = "c9_default") -> str:
    """Create or reuse a browser profile."""
    global _DEFAULT_PROFILE
    if _DEFAULT_PROFILE:
        return _DEFAULT_PROFILE
    # List existing profiles
    try:
        profiles = _get("/profiles").get("profiles", [])
        for p in profiles:
            if p.get("name") == name:
                _DEFAULT_PROFILE = p["id"]
                return _DEFAULT_PROFILE
    except Exception:
        pass
    # Create new profile
    resp = _post("/profiles", {"name": name, "description": "C9 browse bridge default"})
    _DEFAULT_PROFILE = resp["id"]
    return _DEFAULT_PROFILE


def ensure_instance(profile_id: str, mode: str = "headless") -> str:
    """Start a browser instance for the given profile."""
    global _DEFAULT_INSTANCE
    if _DEFAULT_INSTANCE:
        return _DEFAULT_INSTANCE
    resp = _post("/instances/start", {"profileId": profile_id, "mode": mode})
    _DEFAULT_INSTANCE = resp["id"]
    return _DEFAULT_INSTANCE


def ensure_tab(instance_id: str, url: Optional[str] = None) -> str:
    """Open a tab in the instance."""
    global _DEFAULT_TAB
    if _DEFAULT_TAB and not url:
        return _DEFAULT_TAB
    payload = {"url": url} if url else {}
    resp = _post(f"/instances/{instance_id}/tabs/open", payload)
    _DEFAULT_TAB = resp["tabId"]
    return _DEFAULT_TAB


def get_default_tab() -> str:
    """Lazily initialize profile â instance â tab."""
    if _DEFAULT_TAB:
        return _DEFAULT_TAB
    pid = ensure_profile()
    iid = ensure_instance(pid)
    return ensure_tab(iid)


# ââ High-level commands ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def cmd_nav(url: str) -> Dict[str, Any]:
    """Navigate the default tab to a URL."""
    tab_id = get_default_tab()
    resp = _post(f"/tabs/{tab_id}/navigate", {"url": url})
    result = {"command": "nav", "url": url, "tab_id": tab_id, "response": resp}
    _bus_emit("browse_nav", result)
    return result


def cmd_snap(filter_type: Optional[str] = None) -> Dict[str, Any]:
    """Get a structured snapshot of the current page."""
    tab_id = get_default_tab()
    endpoint = f"/tabs/{tab_id}/snapshot"
    if filter_type:
        endpoint += f"?filter={filter_type}"
    resp = _get(endpoint)
    result = {"command": "snap", "tab_id": tab_id, "filter": filter_type, "response": resp}
    _bus_emit("browse_snap", result)
    return result


def cmd_text() -> Dict[str, Any]:
    """Extract token-efficient text from the current page."""
    tab_id = get_default_tab()
    resp = _get(f"/tabs/{tab_id}/text")
    result = {"command": "text", "tab_id": tab_id, "response": resp}
    _bus_emit("browse_text", result)
    return result


def cmd_click(ref: str) -> Dict[str, Any]:
    """Click an element by its accessibility ref (e.g. e5)."""
    tab_id = get_default_tab()
    resp = _post(f"/tabs/{tab_id}/action", {"kind": "click", "ref": ref})
    result = {"command": "click", "ref": ref, "tab_id": tab_id, "response": resp}
    _bus_emit("browse_click", result)
    return result


def cmd_fill(ref: str, value: str) -> Dict[str, Any]:
    """Fill an input element by ref."""
    tab_id = get_default_tab()
    resp = _post(f"/tabs/{tab_id}/action", {"kind": "fill", "ref": ref, "value": value})
    result = {"command": "fill", "ref": ref, "value": value, "tab_id": tab_id, "response": resp}
    _bus_emit("browse_fill", result)
    return result


def cmd_search(query: str) -> Dict[str, Any]:
    """Quick search: nav to DuckDuckGo, grab text results."""
    search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    nav_res = cmd_nav(search_url)
    time.sleep(2)  # Let page settle
    text_res = cmd_text()
    result = {
        "command": "search",
        "query": query,
        "nav": nav_res,
        "text": text_res,
    }
    _bus_emit("browse_search", result)
    return result


def cmd_audit(url: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run a PinchTab site audit (requires CLI, falls back to nav+snap)."""
    # Prefer CLI if available
    import subprocess
    out = output_dir or os.path.expanduser("~/cloud9/audits")
    try:
        subprocess.run(
            ["pinchtab", "audit", url, "--output-dir", out],
            check=True,
            capture_output=True,
            text=True,
        )
        result = {"command": "audit", "url": url, "output_dir": out, "status": "ok"}
    except FileNotFoundError:
        # Fallback: nav + snap + text
        cmd_nav(url)
        time.sleep(2)
        snap = cmd_snap()
        text = cmd_text()
        result = {"command": "audit", "url": url, "snap": snap, "text": text, "status": "fallback"}
    _bus_emit("browse_audit", result)
    return result


# ââ AutoBaby tool interface ââââââââââââââââââââââââââââââââââââââââââââââââââââ

def autobaby_research(topic: str, max_pages: int = 3) -> str:
    """
    AutoBaby-compatible research function.
    Searches for a topic, navigates top result, extracts text.
    Returns a condensed string for feeding to Ollama/Phi-3.
    """
    results = []
    search_res = cmd_search(topic)
    text_data = search_res.get("text", {}).get("response", {})
    extracted = text_data.get("text", text_data.get("content", ""))
    results.append(f"--- Search: {topic} ---\n{extracted[:4000]}")

    # If snap shows links, try first few
    snap = cmd_snap("interactive")
    elements = snap.get("response", {}).get("elements", [])
    links = [e for e in elements if e.get("tag") == "a" and e.get("href")]
    for i, link in enumerate(links[:max_pages]):
        try:
            href = link["href"]
            if href.startswith("http"):
                cmd_nav(href)
                time.sleep(2)
                t = cmd_text()
                txt = t.get("response", {}).get("text", "")
                results.append(f"--- Page {i+1}: {href} ---\n{txt[:3000]}")
        except Exception as e:
            results.append(f"--- Page {i+1}: ERROR {e} ---")

    full = "\n\n".join(results)
    _bus_emit("autobaby_research", {"topic": topic, "pages": max_pages, "char_count": len(full)})
    return full


# ââ CLI ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    cmd = sys.argv[1]
    args = sys.argv[2:]

    try:
        if cmd == "nav":
            _print_json(cmd_nav(args[0]))
        elif cmd == "snap":
            filt = args[0] if args else None
            _print_json(cmd_snap(filt))
        elif cmd == "text":
            _print_json(cmd_text())
        elif cmd == "click":
            _print_json(cmd_click(args[0]))
        elif cmd == "fill":
            _print_json(cmd_fill(args[0], args[1]))
        elif cmd == "search":
            _print_json(cmd_search(" ".join(args)))
        elif cmd == "audit":
            out = args[1] if len(args) > 1 else None
            _print_json(cmd_audit(args[0], out))
        elif cmd == "research":
            # AutoBaby-style research
            topic = " ".join(args)
            print(autobaby_research(topic))
        elif cmd == "status":
            _print_json(_get("/health"))
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            return 1
    except Exception as e:
        err = {"error": str(e), "command": cmd, "args": args}
        _bus_emit("browse_error", err)
        _print_json(err)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
