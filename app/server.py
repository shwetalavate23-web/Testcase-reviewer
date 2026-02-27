"""HTTP server and routes for testcase reviewer without external frameworks."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import parse_qs

from app.parser import parse_zephyr_upload
from app.reviewer import review_testcases


ROOT = Path(__file__).resolve().parent.parent


def _parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], dict[str, dict[str, bytes | str]]]:
    """Parse multipart/form-data payload without cgi dependency."""
    match = re.search(r"boundary=([^;]+)", content_type)
    if not match:
        return {}, {}

    boundary = match.group(1).strip().strip('"').encode("utf-8")
    delimiter = b"--" + boundary
    fields: dict[str, str] = {}
    files: dict[str, dict[str, bytes | str]] = {}

    for part in body.split(delimiter):
        part = part.strip()
        if not part or part == b"--":
            continue

        if b"\r\n\r\n" not in part:
            continue

        headers_blob, content = part.split(b"\r\n\r\n", 1)
        headers = headers_blob.decode("utf-8", errors="replace").split("\r\n")
        header_map: dict[str, str] = {}
        for header in headers:
            if ":" not in header:
                continue
            key, value = header.split(":", 1)
            header_map[key.strip().lower()] = value.strip()

        disposition = header_map.get("content-disposition", "")
        name_match = re.search(r'name="([^"]+)"', disposition)
        if not name_match:
            continue

        field_name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]*)"', disposition)

        # Trim multipart terminators.
        content = content.rstrip(b"\r\n")

        if filename_match:
            files[field_name] = {
                "filename": filename_match.group(1),
                "content": content,
            }
        else:
            fields[field_name] = content.decode("utf-8", errors="replace")

    return fields, files


class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._serve_file(ROOT / "templates" / "index.html", "text/html")
            return
        if self.path.startswith("/static/"):
            target = ROOT / self.path.lstrip("/")
            content_type = "text/plain"
            if target.suffix == ".css":
                content_type = "text/css"
            if target.suffix == ".js":
                content_type = "application/javascript"
            self._serve_file(target, content_type)
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/review":
            self.send_error(404, "Not found")
            return

        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        if "multipart/form-data" in content_type:
            fields, files = _parse_multipart(content_type, body)
            acceptance_criteria = fields.get("acceptance_criteria", "")
            user_story = fields.get("user_story", "")
            file_item = files.get("zephyr_file")
            if file_item is None:
                self._json({"error": "Please upload a Zephyr export file."}, status=400)
                return
            file_bytes = file_item.get("content", b"")
            filename = str(file_item.get("filename") or "upload.csv")
        else:
            params = parse_qs(body.decode("utf-8", errors="replace"))
            acceptance_criteria = params.get("acceptance_criteria", [""])[0]
            user_story = params.get("user_story", [""])[0]
            self._json({"error": "Upload file is required."}, status=400)
            return

        cases = parse_zephyr_upload(file_bytes, filename)
        if not cases:
            self._json({"error": "No test cases found in uploaded file."}, status=400)
            return

        result = review_testcases(cases, acceptance_criteria, user_story)
        self._json(result)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(404, "Not found")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload: dict, status: int = 200) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    server = ThreadingHTTPServer((host, port), ReviewHandler)
    print(f"Server listening on http://{host}:{port}")
    server.serve_forever()
