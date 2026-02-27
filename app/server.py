"""HTTP server and routes for testcase reviewer without external frameworks."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import cgi

from app.parser import parse_zephyr_upload
from app.reviewer import review_testcases


ROOT = Path(__file__).resolve().parent.parent


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
        if "multipart/form-data" in content_type:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
            )
            acceptance_criteria = form.getvalue("acceptance_criteria", "")
            user_story = form.getvalue("user_story", "")
            file_item = form["zephyr_file"] if "zephyr_file" in form else None
            if file_item is None or not file_item.file:
                self._json({"error": "Please upload a Zephyr export file."}, status=400)
                return
            file_bytes = file_item.file.read()
            filename = file_item.filename or "upload.csv"
        else:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            params = parse_qs(body)
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
