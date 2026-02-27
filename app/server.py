"""Flask server for testcase reviewer."""

from __future__ import annotations

from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

from app.parser import parse_zephyr_upload
from app.reviewer import review_testcases


ROOT = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
)


@app.route("/")
def index():
    return send_from_directory(ROOT / "templates", "index.html")


@app.route("/api/review", methods=["POST"])
def review():
    acceptance_criteria = request.form.get("acceptance_criteria", "")
    user_story = request.form.get("user_story", "")

    file = request.files.get("zephyr_file")
    if not file:
        return jsonify({"error": "Please upload a Zephyr export file."}), 400

    file_bytes = file.read()
    filename = file.filename or "upload.csv"

    cases = parse_zephyr_upload(file_bytes, filename)
    if not cases:
        return jsonify({"error": "No test cases found in uploaded file."}), 400

    result = review_testcases(cases, acceptance_criteria, user_story)
    return jsonify(result)


def run_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    print(f"Server running on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)