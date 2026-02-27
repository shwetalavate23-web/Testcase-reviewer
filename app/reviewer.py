"""Review orchestration for test cases and fallback feedback."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.config import settings
from app.coverage import compute_coverage, render_tree
from app.llm import LLMClient


PROMPT_PATH = Path(__file__).parent / "prompts" / "review_prompt.txt"


class ContextRetriever(Protocol):
    def retrieve_context(self, query: str, k: int) -> list[str]:
        ...


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

    bullets.append("- Summary 1: Tighten specificity and these tests move from decent to deadly accurate.")
    bullets.append("- Summary 2: Great momentum—now make every testcase explicit enough to survive handoffs.")
    return "\n".join(bullets)


def _format_testcases(cases: list[dict[str, str]]) -> str:
    rows: list[str] = []
    for idx, case in enumerate(cases, start=1):
        rows.append(
            "\n".join(
                [
                    f"Test Case {idx}",
                    f"Title: {case.get('title', '')}",
                    f"Preconditions: {case.get('preconditions', '')}",
                    f"Test Type: {case.get('test_type', '')}",
                    f"Labels: {case.get('labels', '')}",
                    f"Steps: {case.get('steps', '')}",
                    f"Expected: {case.get('expected', '')}",
                ]
            )
        )
    return "\n\n".join(rows)


def review_testcases(
    cases: list[dict[str, str]],
    acceptance_criteria: str,
    user_story: str,
    retriever: ContextRetriever | None,
) -> dict[str, str | int]:
    base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    testcase_text = _format_testcases(cases)

    context_chunks: list[str] = []
    if retriever is not None:
        query = f"Acceptance Criteria:\n{acceptance_criteria}\n\nUser Story:\n{user_story}\n\n{testcase_text}"
        try:
            context_chunks = retriever.retrieve_context(query, k=settings.retrieval_k)
        except Exception:
            context_chunks = []
    guideline_context = "\n\n".join(context_chunks) if context_chunks else "No guideline context retrieved."

    prompt = (
        f"{base_prompt}\n\n"
        "You are a strict QA testcase reviewer. Follow the provided QA guideline context strictly.\n"
        "Output must be bullet points, humorous-but-professional tone, and exactly two summary lines at the end.\n\n"
        f"Retrieved QA Guideline Context:\n{guideline_context}\n\n"
        f"Acceptance Criteria:\n{acceptance_criteria}\n\n"
        f"User Story:\n{user_story}\n\n"
        f"Testcase Content:\n{testcase_text}\n"
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
