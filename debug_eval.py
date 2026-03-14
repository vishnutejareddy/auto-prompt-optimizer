"""
debug_eval.py — Diagnostic tool for understanding model failures.

Shows actual model output vs expected for each test case.
Use this to identify WHY cases are scoring low, then add
targeted instructions to prompt.md to fix them.

Usage:
  uv run python debug_eval.py           # run all cases
  uv run python debug_eval.py 9 21      # run specific case numbers
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

PROMPT_FILE = Path("prompt.md")
TEST_CASES  = Path("test_cases.json")
GEN_MODEL   = "claude-haiku-4-5-20251001"
JUDGE_MODEL = "claude-sonnet-4-6"

client = Anthropic()

DIVIDER = "─" * 72


def run_prompt(system_prompt: str, user_input: str) -> str:
    resp = client.messages.create(
        model=GEN_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}],
    )
    return resp.content[0].text.strip()


def score_with_judge(output: str, expected: str, task: str) -> tuple[float, str]:
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": f"""You are evaluating an LLM output for a '{task}' task.

Reference analysis (expert benchmark): {expected}
Actual output: {output}

Rate the actual output on a scale of 0.0 to 10.0 based on:
- Verdict clarity (clear investment stance stated upfront)
- Analytical quality (claims grounded in specific numbers from the data)
- Actionability (concrete recommendation a portfolio manager can act on)
- Signal-to-noise (no filler, every sentence adds value)

Reply in this exact format:
SCORE: <number>
REASON: <one sentence explaining the main weakness or strength>""",
            }
        ],
    )
    text = resp.content[0].text.strip()
    score = 0.0
    reason = ""
    for line in text.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
    return score, reason


def debug(case_indices: list[int] | None = None):
    system_prompt = PROMPT_FILE.read_text().strip()
    cases = json.loads(TEST_CASES.read_text())

    if case_indices:
        selected = [(i, cases[i - 1]) for i in case_indices if 1 <= i <= len(cases)]
    else:
        selected = [(i + 1, c) for i, c in enumerate(cases)]

    print(f"\nPrompt ({len(system_prompt)} chars):")
    print(f'  "{system_prompt[:120]}{"..." if len(system_prompt) > 120 else ""}"\n')

    scores = []
    for num, case in selected:
        print(DIVIDER)
        print(f"CASE {num}/{len(cases)}  [{case['task']}]")
        print(f"\nINPUT:\n  {case['input'][:200]}...")
        print(f"\nEXPECTED (excerpt):\n  {case['expected'][:200]}...")

        output = run_prompt(system_prompt, case["input"])
        score, reason = score_with_judge(output, case["expected"], case["task"])
        scores.append(score)

        print(f"\nACTUAL OUTPUT:\n  {output}")
        print(f"\nSCORE: {score}/10")
        print(f"JUDGE: {reason}")

    print(DIVIDER)
    if len(scores) > 1:
        avg = sum(scores) / len(scores)
        print(f"\nAVERAGE: {avg:.3f}/10 across {len(scores)} cases")


if __name__ == "__main__":
    indices = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
    debug(indices)
