"""
eval.py — Fixed evaluator. The agent must NEVER modify this file.

Runs the current prompt.md against all test cases and prints a score.
Uses claude-haiku for generation (cheap/fast) and claude-sonnet as judge.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

PROMPT_FILE  = Path("prompt.md")
TEST_CASES   = Path("test_cases.json")
RESULTS_FILE = Path("results.tsv")
GEN_MODEL    = "claude-haiku-4-5-20251001"
JUDGE_MODEL  = "claude-sonnet-4-6"

client = Anthropic()


def run_prompt(system_prompt: str, user_input: str) -> str:
    resp = client.messages.create(
        model=GEN_MODEL,
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}],
    )
    return resp.content[0].text.strip()


def score_with_judge(output: str, expected: str, task: str) -> float:
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=16,
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

Reply with ONLY a number between 0.0 and 10.0. No explanation.""",
            }
        ],
    )
    try:
        return float(resp.content[0].text.strip())
    except ValueError:
        return 0.0


def evaluate(hypothesis: str = "") -> float:
    system_prompt = PROMPT_FILE.read_text().strip()
    cases = json.loads(TEST_CASES.read_text())

    scores = []
    for i, case in enumerate(cases, 1):
        output = run_prompt(system_prompt, case["input"])
        score  = score_with_judge(output, case["expected"], case["task"])
        scores.append(score)
        print(f"  Case {i}/{len(cases)}: {score:.1f}/10")

    avg = sum(scores) / len(scores)

    # Append to results log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, "a") as f:
        if not RESULTS_FILE.exists() or RESULTS_FILE.stat().st_size == 0:
            f.write("timestamp\tscore\thypothesis\tresult\n")
        f.write(f"{timestamp}\t{avg:.3f}\t{hypothesis}\tPENDING\n")

    print(f"SCORE: {avg:.3f}")
    return avg


if __name__ == "__main__":
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else ""
    evaluate(hypothesis)
