"""Coverage scoring and tree rendering utilities."""


def compute_coverage(test_cases_count: int, acceptance_criteria: str) -> int:
    criteria_items = [line.strip("- •\t ") for line in acceptance_criteria.splitlines() if line.strip()]
    criteria_count = max(1, len(criteria_items))
    estimated_covered = min(test_cases_count, criteria_count)
    return round((estimated_covered / criteria_count) * 100)


def render_tree(coverage: int) -> str:
    leaf_count = max(1, min(10, coverage // 10))
    leaves = "🍃" * leaf_count
    fruit = " 🍎" if coverage == 100 else ""
    return (
        "    |||\n"
        f"  {leaves}{fruit}\n"
        "    |||\n"
        "    |||"
    )
