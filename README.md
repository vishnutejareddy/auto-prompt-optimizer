# Auto-Prompt Optimizer

An autonomous prompt engineering framework inspired by [autoresearch](https://github.com/karpathy/autoresearch). An AI agent iteratively modifies a system prompt, evaluates it against a fixed test suite, and keeps only improvements — running overnight without human intervention.

## How It Works

```
Agent reads prompt.md
  → hypothesizes one improvement
  → edits prompt.md
  → runs: python eval.py
  → if score improves: git commit, keep
  → if score drops: git checkout, discard
  → repeat
```

- **`prompt.md`** — the prompt being optimized (agent modifies this)
- **`eval.py`** — fixed evaluator, never modified (uses Claude Haiku to generate, Claude Sonnet as judge)
- **`test_cases.json`** — fixed test suite
- **`program.md`** — agent instructions (the loop, techniques to try)
- **`results.tsv`** — experiment log (score, hypothesis, KEPT/DISCARDED)

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/vishnutejareddy/auto-prompt-optimizer
cd auto-prompt-optimizer
uv sync
```

> Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

**2. Add your Anthropic API key**

Create a `.env` file in the project root:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

> Get your API key at [console.anthropic.com](https://console.anthropic.com). The `.env` file is gitignored and will never be committed.

**3. Run the baseline eval**

```bash
uv run python eval.py "baseline"
```

This scores the starting `prompt.md` and logs it to `results.tsv`.

**4. Start the optimization loop**

Open Claude Code in the project directory and say:

```
read program.md and start the optimization loop
```

The agent will run continuously, trying techniques from `program.md` and committing improvements to git.

## Customizing for Your Use Case

**Change the task** — Edit `test_cases.json` with your own input/expected pairs and update `prompt.md` with a starting prompt for your task (e.g., code generation, classification, SQL writing).

**Change the model** — Edit `GEN_MODEL` and `JUDGE_MODEL` in `eval.py`.

**Change the scoring** — Edit the judge prompt in `score_with_judge()` in `eval.py` to emphasize what matters for your task.

## Viewing Results

```bash
cat results.tsv
```

Or track progress in git:

```bash
git log --oneline
```

## Project Structure

```
auto-prompt-optimizer/
├── prompt.md          # Current prompt (agent modifies this)
├── eval.py            # Fixed evaluator — never touch this
├── test_cases.json    # Fixed test suite
├── program.md         # Agent instructions
├── update_result.py   # Helper to mark results KEPT/DISCARDED
├── results.tsv        # Experiment log (gitignored after baseline)
└── .env               # Your API key (gitignored)
```
