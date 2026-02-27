# QA Testcase Review Guidelines

## Core Quality Rules
- Every testcase must include a clear and specific title that identifies behavior under test.
- Preconditions should describe system state, required data, and user permissions.
- Steps must be atomic, ordered, and reproducible by another tester.
- Expected results must be objective and verifiable.
- Negative and edge scenarios should be represented where applicable.

## Coverage Rules
- Acceptance criteria should map to one or more testcases.
- Include positive, negative, and boundary validation for important flows.
- Mark test type explicitly (smoke, regression, integration, etc.).
- Add labels/tags for feature area and risk level.

## Writing Style
- Use concise language and avoid ambiguity.
- Prefer deterministic assertions over subjective outcomes.
- Avoid combining multiple validations into one step unless necessary.
