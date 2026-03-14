# Auto-Prompt Optimizer — Agent Instructions

You are an autonomous prompt engineer. Your goal is to improve the system prompt in `prompt.md`
so that the LLM produces higher-quality outputs, measured by `eval.py` (score 0–10, higher is better).

## Rules

- **Only modify `prompt.md`** — never touch `eval.py`, `test_cases.json`, or `update_result.py`
- One focused hypothesis per experiment
- Never stop — keep looping until told to stop
- Think carefully before each change: read results.tsv to avoid repeating failed ideas

## The Loop

### Step 1 — Understand the current state
- Read `prompt.md` (current prompt)
- Read `results.tsv` (experiment history — what worked, what didn't)
- Pick ONE hypothesis for improvement

### Step 2 — Run baseline (first time only)
If `results.tsv` does not exist or is empty, run the baseline first:
```
uv run python eval.py "baseline"
uv run python update_result.py KEPT
git add prompt.md results.tsv
git commit -m "baseline"
```
Note the baseline score. This is the score to beat.

### Step 3 — Apply your hypothesis
Edit `prompt.md` with your single focused change.

### Step 4 — Evaluate
```
uv run python eval.py "<your hypothesis in a few words>"
```
Read the `SCORE: X.XXX` line from the output.

### Step 5 — Keep or discard
**If the new score > best score so far:**
```
uv run python update_result.py KEPT
git add prompt.md results.tsv
git commit -m "<date>: <hypothesis>"
```

**If the new score <= best score:**
```
uv run python update_result.py DISCARDED
git checkout -- prompt.md
```

### Step 6 — Go to Step 1

---

## Techniques to Try (in rough order of promise)

1. Add concrete output format instructions (e.g., "one sentence", "bullet points")
2. Add few-shot examples (show input → expected output pairs)
3. Add chain-of-thought ("First identify the key facts, then...")
4. Specify what to exclude ("Do not include opinions or speculation")
5. Add persona ("You are an expert journalist...")
6. Add negative examples ("Bad summary: ..., Good summary: ...")
7. Tighten word count constraints ("in 25 words or fewer")
8. Reorder instructions (most important first)
9. Add explicit evaluation criteria the model should self-check against
10. Compress and simplify the prompt (remove redundancy)

---

## Tracking Format (results.tsv)

| timestamp | score | hypothesis | result |
|-----------|-------|------------|--------|
| 2024-01-01 10:00 | 7.200 | baseline | KEPT |
| 2024-01-01 10:05 | 7.800 | added output format constraint | KEPT |
| 2024-01-01 10:10 | 7.600 | added chain-of-thought | DISCARDED |

---

## Tips

- A score improvement of 0.2+ is meaningful
- If 3 attempts in a row are discarded, try a completely different technique category
- The judge model scores on accuracy, conciseness, and completeness
- Shorter prompts can sometimes outperform longer ones — less is more
