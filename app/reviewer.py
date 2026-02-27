"""Review orchestration for test cases and fallback feedback."""

from __future__ import annotations

from pathlib import Path

from app.coverage import compute_coverage, render_tree
from app.llm import LLMClient


PROMPT_PATH = Path(__file__).parent / "prompts" / "review_prompt.txt"


def _heuristic_review(cases: list[dict[str, str]]) -> str:
    bullets: list[str] = []
    for i, case in enumerate(cases, start=1):
        title = case.get("title", "")
        steps = case.get("steps", "")
        expected = case.get("expected", "")
        test_type = case.get("test_type", "")
        preconditions = case.get("preconditions", "")
        labels = case.get("labels", "")

        if len(title) < 10:
            bullets.append(f"- TC{i}: Title is tiny; give it enough detail so future-you doesn't need detective mode.")
        else:
            bullets.append(f"- TC{i}: Title is clear and readable—nice start.")

        if len(steps.splitlines()) < 2 and len(steps.split(".")) < 3:
            bullets.append(f"- TC{i}: Steps look compact; split actions into atomic steps for easier debugging.")
        if not expected:
            bullets.append(f"- TC{i}: Expected result is missing—this test currently grades itself on vibes.")
        if not test_type:
            bullets.append(f"- TC{i}: Add a test type so reports can separate smoke from full-course regression.")
        if not preconditions:
            bullets.append(f"- TC{i}: Preconditions are absent; setup context helps avoid flaky surprises.")
        if not labels:
            bullets.append(f"- TC{i}: Labels are empty; tags make triage and analytics way faster.")

    bullets.append("- Roast 1: These tests are close to greatness—they just need less mystery and more specificity.")
    bullets.append("- Roast 2: Your coverage ambition is strong; your metadata just called asking for equal attention.")
    return "\n".join(bullets)


def review_testcases(cases: list[dict[str, str]], acceptance_criteria: str, user_story: str) -> dict[str, str | int]:
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{base_prompt}\n\n"
        f"Acceptance Criteria:\n{acceptance_criteria}\n\n"
        f"User Story:\n{user_story}\n\n"
        f"Test Cases:\n{cases}\n"
    )

    llm_output = ""
    try:
        llm_output = LLMClient().generate(prompt)
    except Exception:
        llm_output = ""

    coverage = compute_coverage(len(cases), acceptance_criteria)
    tree = render_tree(coverage)

    return {
        "review": llm_output.strip() or _heuristic_review(cases),
        "coverage": coverage,
        "tree": tree,
    }
