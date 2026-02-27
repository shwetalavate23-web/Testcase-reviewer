# Zephyr Testcase Reviewer

A lightweight web app that reviews Zephyr-exported test cases against QA documentation guidelines.

## Features
- Accepts Acceptance Criteria and User Story input
- Uploads Zephyr exports (`.csv` or `.json`)
- Produces bullet-point feedback with a humorous-but-professional style
- Adds two light-hearted roast lines at the end
- Computes coverage percentage and displays a tree (🍎 appears at 100%)

## Setup
1. Create virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy environment template:
   ```bash
   cp .env.example .env
   ```
3. Run app:
   ```bash
   python run_web.py
   ```
4. Open `http://localhost:5000`

## Project Structure
- `app/config.py`: environment settings
- `app/prompts/review_prompt.txt`: prompt template
- `app/parser.py`: Zephyr file parsing
- `app/reviewer.py`: review orchestration and fallback heuristics
- `app/server.py`: HTTP server routes
- `run_web.py`: web app launcher
