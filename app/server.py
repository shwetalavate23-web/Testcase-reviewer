"""Flask server for testcase reviewer."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory

from app.parser import parse_zephyr_upload
from app.reviewer import review_testcases


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "output.md"

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
    _write_output_markdown(filename, acceptance_criteria, user_story, result)
    result["output_file"] = OUTPUT_PATH.name
    return jsonify(result)


def _write_output_markdown(
    filename: str,
    acceptance_criteria: str,
    user_story: str,
    result: dict[str, str | int],
) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    output = (
        "# Testcase Review Output\n\n"
        f"- Generated at: {timestamp}\n"
        f"- Source file: {filename}\n"
        f"- Coverage: {result['coverage']}%\n\n"
        "## Acceptance Criteria\n\n"
        f"{acceptance_criteria.strip() or '_Not provided_'}\n\n"
        "## User Story\n\n"
        f"{user_story.strip() or '_Not provided_'}\n\n"
        "## Review Comments\n\n"
        f"{result['review']}\n\n"
        "## Coverage Tree\n\n"
        "```\n"
        f"{result['tree']}\n"
        "```\n"
    )
    OUTPUT_PATH.write_text(output, encoding="utf-8")


def run_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    print(f"Server running on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
