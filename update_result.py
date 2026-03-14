"""
update_result.py — Updates the last PENDING result in results.tsv to KEPT or DISCARDED.
Usage: python update_result.py KEPT
       python update_result.py DISCARDED
"""

import sys
from pathlib import Path

RESULTS_FILE = Path("results.tsv")


def update_last(result: str):
    if not RESULTS_FILE.exists():
        print("No results.tsv found.")
        sys.exit(1)

    lines = RESULTS_FILE.read_text().splitlines()
    for i in range(len(lines) - 1, 0, -1):
        if lines[i].endswith("\tPENDING"):
            lines[i] = lines[i][: -len("PENDING")] + result
            break

    RESULTS_FILE.write_text("\n".join(lines) + "\n")
    print(f"Updated last result to {result}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("KEPT", "DISCARDED"):
        print("Usage: python update_result.py KEPT|DISCARDED")
        sys.exit(1)
    update_last(sys.argv[1])
