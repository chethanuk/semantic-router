#!/usr/bin/env python3
"""Reference-integrity guard for issue #2585.

train-domain.sh and its AWS / per-domain YAML docs were never functional in
this tree (assets never committed). This check is the executable form of the
plan's gate: zero residual references may reappear under cache_embeddings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEAD_REF = re.compile(
    r"deploy-vllm|train-domain\.sh|TEMPLATE\.yaml|QUICK_START_AWS|"
    r"Domain Config Reference|data_file|output_dir|hf_repo|vllm_model|"
    r"<domain>\.yaml"
)


def collect_hits() -> list[str]:
    hits: list[str] = []
    for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.sh")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if DEAD_REF.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{lineno}:{line.strip()}")
    return hits


def main() -> int:
    script = ROOT / "train-domain.sh"
    if script.exists():
        print(f"FAIL: {script} still exists", file=sys.stderr)
        return 1
    hits = collect_hits()
    if hits:
        print(f"FAIL: {len(hits)} dead AWS/train-domain reference(s):", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1
    print("PASS: train-domain.sh retired; zero dead AWS references under cache_embeddings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
