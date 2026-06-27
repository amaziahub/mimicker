import argparse
import json
import signal
import sys
from unittest.mock import MagicMock, patch

import pytest

from mimicker.cli import (
    _parse_inline_stub,
    cmd_report,
    cmd_serve,
    cmd_validate,
    cmd_wait,
    main,
    _print_github_summary,
    _print_text_report,
)
from mimicker.mimicker import mimicker
from tests.support.client import Client


# ── _parse_inline_stub ────────────────────────────────────────────────────────

def test_parse_inline_stub_get():
    route = _parse_inline_stub('GET /hello -> 200 {"msg": "hi"}')
    cfg = route.build()
    assert cfg["method"] == "GET"
    assert cfg["path"] == "/hello"
    assert cfg["status"] == 200
    assert cfg["body"] == {"msg": "hi"}


def test_parse_inline_stub_no_body():
    route = _parse_inline_stub("POST /submit -> 201")
    cfg = route.build()
    assert cfg["method"] == "POST"
    assert cfg["status"] == 201


def test_parse_inline_stub_delete():
    route = _parse_inline_stub("DELETE /resource/1 -> 204")
    cfg = route.build()
    assert cfg["method"] == "DELETE"
    assert cfg["status"] == 204


def test_parse_inline_stub_invalid_exits():
    with pytest.raises(SystemExit):
        _parse_inline_stub("not valid syntax at all")


def test_parse_inline_stub_non_json_body():
    route = _parse_inline_stub("GET /greet -> 200 plain-text")
    cfg = route.build()
    assert cfg["body"] == "plain-text"


# ── cmd_validate ──────────────────────────────────────────────────────────────

def test_validate_valid_yaml(tmp_path):
    stub_file = tmp_path / "stubs.yaml"
    stub_file.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /hello\n"
        "    status: 200\n"
    )
    with patch("sys.exit") as mock_exit:
        cmd_validate(argparse.Namespace(file=str(stub_file)))
    mock_exit.assert_not_called()


def test_validate_valid_json(tmp_path):
    stub_file = tmp_path / "stubs.json"
    stub_file.write_text(json.dumps({
        "routes": [{"method": "GET", "path": "/x", "status": 200}]
    }))
    with patch("sys.exit") as mock_exit:
        cmd_validate(argparse.Namespace(file=str(stub_file)))
    mock_exit.assert_not_called()


def test_validate_missing_file_exits():
    with pytest.raises(SystemExit) as exc_info:
        cmd_validate(argparse.Namespace(file="/tmp/mimicker-no-such-file-xyz.yaml"))
    assert exc_info.value.code == 1


def test_validate_invalid_config_exits(tmp_path):
    stub_file = tmp_path / "bad.yaml"
    stub_file.write_text("routes:\n  - method: BADMETHOD\n    path: /x\n    status: 200\n")
    with pytest.raises(SystemExit) as exc_info:
        cmd_validate(argparse.Namespace(file=str(stub_file)))
    assert exc_info.value.code == 1


def test_validate_parse_error_exits(tmp_path):
    stub_file = tmp_path / "broken.yaml"
    stub_file.write_text("{not: valid: yaml: [")
    with pytest.raises(SystemExit) as exc_info:
        cmd_validate(argparse.Namespace(file=str(stub_file)))
    assert exc_info.value.code == 1


# ── cmd_report formatters ─────────────────────────────────────────────────────

_SAMPLE_REPORT = {
    "summary": {"total_stubs": 2, "matched_stubs": 1, "unmatched_requests": 1},
    "stubs": [
        {"method": "GET", "path": "/used", "hit_count": 3},
        {"method": "GET", "path": "/unused", "hit_count": 0},
    ],
    "unused_stubs": [{"method": "GET", "path": "/unused"}],
    "unmatched_requests": [
        {"method": "GET", "path": "/unknown", "timestamp": "2024-01-01T00:00:00Z"}
    ],
}


def test_text_report_contains_summary(capsys):
    _print_text_report(_SAMPLE_REPORT)
    out = capsys.readouterr().out
    assert "1/2" in out
    assert "Unmatched" in out


def test_text_report_lists_unused_stubs(capsys):
    _print_text_report(_SAMPLE_REPORT)
    out = capsys.readouterr().out
    assert "/unused" in out


def test_text_report_lists_unmatched_requests(capsys):
    _print_text_report(_SAMPLE_REPORT)
    out = capsys.readouterr().out
    assert "/unknown" in out


def test_github_summary_is_markdown(capsys):
    _print_github_summary(_SAMPLE_REPORT)
    out = capsys.readouterr().out
    assert "##" in out
    assert "|" in out
    assert "/used" in out
    assert "/unused" in out


def test_github_summary_includes_unmatched_table(capsys):
    _print_github_summary(_SAMPLE_REPORT)
    out = capsys.readouterr().out
    assert "/unknown" in out
    assert "Contract Drift" in out


# ── cmd_report integration ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def report_server():
    server = mimicker(port=0)
    from mimicker.mimicker import get
    server.routes(get("/report-test").status(200).body({"ok": True}))
    yield server
    server.shutdown()


def test_cmd_report_text_format(report_server, capsys):
    port = report_server.get_port()
    args = argparse.Namespace(
        url=f"http://localhost:{port}",
        format="text",
        fail_on_unmatched=False,
    )
    with patch("sys.exit"):
        cmd_report(args)
    out = capsys.readouterr().out
    assert "Mimicker Report" in out


def test_cmd_report_json_format(report_server, capsys):
    port = report_server.get_port()
    args = argparse.Namespace(
        url=f"http://localhost:{port}",
        format="json",
        fail_on_unmatched=False,
    )
    with patch("sys.exit"):
        cmd_report(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "summary" in data


def test_cmd_report_github_summary_format(report_server, capsys):
    port = report_server.get_port()
    args = argparse.Namespace(
        url=f"http://localhost:{port}",
        format="github-summary",
        fail_on_unmatched=False,
    )
    with patch("sys.exit"):
        cmd_report(args)
    out = capsys.readouterr().out
    assert "##" in out


def test_cmd_report_fail_on_unmatched_exits_when_drift(report_server):
    port = report_server.get_port()
    # Trigger an unmatched request
    Client(f"http://localhost:{port}").get("/this-path-does-not-exist-zzz")
    args = argparse.Namespace(
        url=f"http://localhost:{port}",
        format="text",
        fail_on_unmatched=True,
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_report(args)
    assert exc_info.value.code == 1


# ── server.load_config integration ───────────────────────────────────────────

# ── cmd_report error path ─────────────────────────────────────────────────────

def test_cmd_report_unreachable_exits():
    args = argparse.Namespace(
        url="http://localhost:19998",
        format="text",
        fail_on_unmatched=False,
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_report(args)
    assert exc_info.value.code == 1


# ── cmd_serve ─────────────────────────────────────────────────────────────────

def _make_mock_server(join_effect=None):
    mock_server = MagicMock()
    if join_effect:
        mock_server._thread.join.side_effect = join_effect
    else:
        mock_server._thread.join.return_value = None
    return mock_server


def test_cmd_serve_default_port():
    args = argparse.Namespace(port=None, config=None, stub=None)
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.assert_called_once_with(8080)


def test_cmd_serve_custom_port():
    args = argparse.Namespace(port=9191, config=None, stub=None)
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.assert_called_once_with(9191)


def test_cmd_serve_keyboard_interrupt_shuts_down():
    args = argparse.Namespace(port=8080, config=None, stub=None)
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_server = _make_mock_server(join_effect=KeyboardInterrupt)
        mock_mimicker.return_value = mock_server
        cmd_serve(args)
    mock_server.shutdown.assert_called_once()


def test_cmd_serve_sigterm_handler_calls_shutdown():
    args = argparse.Namespace(port=8080, config=None, stub=None)
    captured = {}

    def capture_signal(sig, handler):
        captured[sig] = handler

    with patch("mimicker.cli.mimicker") as mock_mimicker, \
         patch("signal.signal", side_effect=capture_signal):
        mock_server = _make_mock_server()
        mock_mimicker.return_value = mock_server
        cmd_serve(args)

    with pytest.raises(SystemExit) as exc_info:
        captured[signal.SIGTERM]()
    assert exc_info.value.code == 0
    mock_server.shutdown.assert_called()


def test_cmd_serve_with_config_file(tmp_path):
    stub_file = tmp_path / "stubs.yaml"
    stub_file.write_text("routes:\n  - method: GET\n    path: /cfg\n    status: 200\n")
    args = argparse.Namespace(port=None, config=str(stub_file), stub=None)
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.return_value.routes.assert_called_once()


def test_cmd_serve_port_from_config(tmp_path):
    stub_file = tmp_path / "stubs.yaml"
    stub_file.write_text("port: 7777\nroutes:\n  - method: GET\n    path: /x\n    status: 200\n")
    args = argparse.Namespace(port=None, config=str(stub_file), stub=None)
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.assert_called_once_with(7777)


def test_cmd_serve_with_inline_stub():
    args = argparse.Namespace(port=8080, config=None, stub="GET /x -> 200")
    with patch("mimicker.cli.mimicker") as mock_mimicker, patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.return_value.routes.assert_called_once()


def test_cmd_serve_config_not_found_exits():
    args = argparse.Namespace(port=None, config="/no/such/file.yaml", stub=None)
    with pytest.raises(SystemExit) as exc_info:
        cmd_serve(args)
    assert exc_info.value.code == 1


def test_cmd_serve_invalid_config_exits(tmp_path):
    stub_file = tmp_path / "bad.yaml"
    stub_file.write_text("routes:\n  - method: NOTVALID\n    path: /x\n    status: 200\n")
    args = argparse.Namespace(port=None, config=str(stub_file), stub=None)
    with pytest.raises(SystemExit) as exc_info:
        cmd_serve(args)
    assert exc_info.value.code == 1


def test_cmd_serve_malformed_config_exits(tmp_path):
    stub_file = tmp_path / "broken.yaml"
    stub_file.write_text("{not: valid: yaml: [")
    args = argparse.Namespace(port=None, config=str(stub_file), stub=None)
    with pytest.raises(SystemExit) as exc_info:
        cmd_serve(args)
    assert exc_info.value.code == 1


def test_cmd_serve_auto_detects_config():
    args = argparse.Namespace(port=None, config=None, stub=None)
    with patch("os.path.exists", return_value=True), \
         patch("mimicker.cli.load_config", return_value={"routes": []}), \
         patch("mimicker.cli.validate_config", return_value=[]), \
         patch("mimicker.cli.build_routes", return_value=[]), \
         patch("mimicker.cli.mimicker") as mock_mimicker, \
         patch("signal.signal"):
        mock_mimicker.return_value = _make_mock_server()
        cmd_serve(args)
    mock_mimicker.assert_called_once_with(8080)


# ── cmd_wait ──────────────────────────────────────────────────────────────────

def test_cmd_wait_success():
    server = mimicker(0)
    port = server.get_port()
    args = argparse.Namespace(url=f"http://localhost:{port}", timeout=5.0)
    with pytest.raises(SystemExit) as exc_info:
        cmd_wait(args)
    assert exc_info.value.code == 0
    server.shutdown()


def test_cmd_wait_timeout_exits():
    args = argparse.Namespace(url="http://localhost:19997", timeout=0.4)
    with pytest.raises(SystemExit) as exc_info:
        cmd_wait(args)
    assert exc_info.value.code == 1


# ── main() ────────────────────────────────────────────────────────────────────

def test_main_dispatches_serve():
    with patch("mimicker.cli.cmd_serve") as mock_cmd, \
         patch("sys.argv", ["mimicker", "serve", "--port", "9191"]):
        main()
    mock_cmd.assert_called_once()


def test_main_dispatches_wait():
    with patch("mimicker.cli.cmd_wait") as mock_cmd, \
         patch("sys.argv", ["mimicker", "wait", "--url", "http://localhost:8080"]):
        main()
    mock_cmd.assert_called_once()


def test_main_dispatches_validate(tmp_path):
    stub_file = tmp_path / "s.yaml"
    stub_file.write_text("routes:\n  - method: GET\n    path: /x\n    status: 200\n")
    with patch("sys.argv", ["mimicker", "validate", str(stub_file)]):
        main()


def test_main_dispatches_report():
    with patch("mimicker.cli.cmd_report") as mock_cmd, \
         patch("sys.argv", ["mimicker", "report", "--url", "http://localhost:8080"]):
        main()
    mock_cmd.assert_called_once()


def test_main_no_subcommand_exits():
    with patch("sys.argv", ["mimicker"]), pytest.raises(SystemExit):
        main()


# ── server.load_config and tracker ───────────────────────────────────────────

def test_server_load_config_from_yaml(tmp_path):
    p = tmp_path / "stubs.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /from-yaml\n"
        "    status: 202\n"
        "    body:\n"
        "      source: yaml\n"
    )
    server = mimicker(port=0)
    server.load_config(str(p))
    port = server.get_port()
    resp = Client(f"http://localhost:{port}").get("/from-yaml")
    assert resp.status_code == 202
    assert resp.json()["source"] == "yaml"
    server.shutdown()


def test_server_load_config_invalid_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("routes:\n  - method: NOTVALID\n    path: /x\n    status: 200\n")
    server = mimicker(port=0)
    with pytest.raises(ValueError, match="Invalid config"):
        server.load_config(str(p))
    server.shutdown()


def test_server_tracker_property():
    server = mimicker(port=0)
    from mimicker.tracking import RequestTracker
    assert isinstance(server.tracker, RequestTracker)
    server.shutdown()
