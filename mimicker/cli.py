import argparse
import json
import os
import re
import signal
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

from mimicker.config import build_routes, load_config, validate_config
from mimicker.logger import get_logger
from mimicker.mimicker import mimicker
from mimicker.route import Route

_HEALTH_PATH = "/__mimicker__/health"
_REPORT_PATH = "/__mimicker__/report"
_AUTO_CONFIG_PATH = "/config/stubs.yaml"


def cmd_serve(args):
    port = args.port
    routes = []

    # Auto-detect config if not specified
    config_path = args.config
    if not config_path and os.path.exists(_AUTO_CONFIG_PATH):
        config_path = _AUTO_CONFIG_PATH
        get_logger().info("Auto-loading config from %s", _AUTO_CONFIG_PATH)

    if config_path:
        try:
            data = load_config(config_path)
        except FileNotFoundError:
            print(f"[ERROR] Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to parse config file: {e}", file=sys.stderr)
            sys.exit(1)

        errors = validate_config(data)
        if errors:
            for e in errors:
                print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

        routes = build_routes(data)
        if port is None:
            port = int(data.get("port", 8080))

    if port is None:
        port = 8080

    if args.stub:
        route = _parse_inline_stub(args.stub)
        routes.append(route)

    server = mimicker(port)
    if routes:
        server.routes(*routes)

    get_logger().info("Serving on port %d. Press Ctrl+C to stop.", port)

    def _shutdown(*_):
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    try:
        server._thread.join()
    except KeyboardInterrupt:
        server.shutdown()


def cmd_wait(args):
    url = args.url.rstrip("/") + _HEALTH_PATH
    deadline = time.monotonic() + args.timeout
    last_error: Optional[Exception] = None

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    print(f"[OK] Mimicker is ready at {args.url}")
                    sys.exit(0)
        except Exception as exc:
            last_error = exc
        time.sleep(0.2)

    print(
        f"[ERROR] Mimicker not ready after {args.timeout}s at {args.url}: {last_error}",
        file=sys.stderr,
    )
    sys.exit(1)


def cmd_validate(args):
    try:
        data = load_config(args.file)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to parse config: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_config(data)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        print(f"\nValidation failed with {len(errors)} error(s).", file=sys.stderr)
        sys.exit(1)

    route_count = len(data.get("routes", []))
    print(f"[OK] {args.file} is valid ({route_count} route(s) defined)")


def cmd_report(args):
    url = args.url.rstrip("/") + _REPORT_PATH
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"[ERROR] Could not reach Mimicker at {args.url}: {e}", file=sys.stderr)
        sys.exit(1)

    fmt = args.format
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "github-summary":
        _print_github_summary(data)
    else:
        _print_text_report(data)

    if args.fail_on_unmatched and data["summary"]["unmatched_requests"] > 0:
        sys.exit(1)


# ── formatters ────────────────────────────────────────────────────────────────

def _print_text_report(data: dict):
    s = data["summary"]
    print(f"\nMimicker Report")
    print(f"  Stubs      : {s['matched_stubs']}/{s['total_stubs']} exercised")
    print(f"  Unmatched  : {s['unmatched_requests']} request(s)")

    if data["unused_stubs"]:
        print("\nUnused stubs (never hit):")
        for stub in data["unused_stubs"]:
            print(f"  - {stub['method']} {stub['path']}")

    if data["unmatched_requests"]:
        print("\nUnmatched requests (contract drift):")
        for req in data["unmatched_requests"]:
            print(f"  - {req['method']} {req['path']}  [{req['timestamp']}]")


def _print_github_summary(data: dict):
    s = data["summary"]
    print("## Mimicker Stub Coverage\n")
    status_icon = "✅" if s["unmatched_requests"] == 0 else "⚠️"
    print(
        f"{status_icon} **{s['matched_stubs']}/{s['total_stubs']}** stubs exercised"
        f" &nbsp;|&nbsp; **{s['unmatched_requests']}** unmatched request(s)\n"
    )

    print("### Stub Coverage\n")
    print("| Method | Path | Hits |")
    print("|--------|------|-----:|")
    for stub in data["stubs"]:
        icon = "✅" if stub["hit_count"] > 0 else "❌"
        print(f"| `{stub['method']}` | `{stub['path']}` | {icon} {stub['hit_count']} |")

    if data["unmatched_requests"]:
        print("\n### Unmatched Requests (Contract Drift)\n")
        print("| Method | Path | Timestamp |")
        print("|--------|------|-----------|")
        for req in data["unmatched_requests"]:
            print(f"| `{req['method']}` | `{req['path']}` | {req['timestamp']} |")


# ── inline stub parser ────────────────────────────────────────────────────────

def _parse_inline_stub(stub_str: str) -> Route:
    """Parse inline stub syntax: 'METHOD /path -> STATUS {json_body}'"""
    m = re.match(r'^(\w+)\s+(/\S*)\s+->\s+(\d+)(?:\s+(.+))?$', stub_str.strip())
    if not m:
        print(
            "[ERROR] Invalid --stub format. Expected: 'METHOD /path -> STATUS {json}'",
            file=sys.stderr,
        )
        sys.exit(1)

    method, path, status, body_str = (
        m.group(1).upper(), m.group(2), int(m.group(3)), m.group(4)
    )
    route = Route(method, path).status(status)
    if body_str:
        try:
            route.body(json.loads(body_str))
        except json.JSONDecodeError:
            route.body(body_str)
    return route


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="mimicker",
        description="Mimicker — lightweight HTTP mock server",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # serve
    p_serve = sub.add_parser("serve", help="Start the mock server")
    p_serve.add_argument(
        "--port", type=int, default=None,
        help="Port to listen on (default: 8080, or value from config file)"
    )
    p_serve.add_argument("--config", metavar="FILE", help="YAML or JSON stub config file")
    p_serve.add_argument(
        "--stub", metavar="STUB",
        help="Inline stub: 'METHOD /path -> STATUS {json}'"
    )

    # wait
    p_wait = sub.add_parser(
        "wait", help="Poll the health endpoint until the server is ready"
    )
    p_wait.add_argument(
        "--url", default="http://localhost:8080",
        help="Server base URL (default: http://localhost:8080)"
    )
    p_wait.add_argument(
        "--timeout", type=float, default=10.0,
        help="Maximum seconds to wait (default: 10)"
    )

    # validate
    p_val = sub.add_parser(
        "validate", help="Validate a stub config file without starting a server"
    )
    p_val.add_argument("file", help="YAML or JSON stub config file to validate")

    # report
    p_rep = sub.add_parser(
        "report", help="Fetch and display the stub coverage/drift report"
    )
    p_rep.add_argument(
        "--url", default="http://localhost:8080",
        help="Server base URL (default: http://localhost:8080)"
    )
    p_rep.add_argument(
        "--format", choices=["text", "json", "github-summary"], default="text",
        help="Output format (default: text)"
    )
    p_rep.add_argument(
        "--fail-on-unmatched", action="store_true",
        help="Exit non-zero if any requests were unmatched (for CI gates)"
    )

    args = parser.parse_args()
    {
        "serve": cmd_serve,
        "wait": cmd_wait,
        "validate": cmd_validate,
        "report": cmd_report,
    }[args.command](args)


if __name__ == "__main__":
    main()
