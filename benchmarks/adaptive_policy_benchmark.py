"""Reproducible, model-free benchmark for the adaptive policy.

This measures policy-selection overhead and the effective target reduction
requested for a fixed coding-agent workload matrix. It intentionally does
not fabricate LLM task-success numbers; model-backed evaluation can consume
this same matrix later.
"""
from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

from headroom.adaptive_policy import AdaptivePolicy

CASES = [
    ("code", "search", 0.50),
    ("code", "debug", 0.80),
    ("json", "search", 0.20),
    ("json", "debug", 0.70),
    ("text", "summary", 0.20),
    ("text", "debug", 0.70),
] * 20


def main() -> None:
    policy = AdaptivePolicy()
    rows = []
    for content, task, expected in CASES:
        t0 = time.perf_counter_ns()
        actual = policy.get_level(content, task)
        elapsed_us = (time.perf_counter_ns() - t0) / 1000
        rows.append({"content": content, "task": task, "expected_keep_ratio": expected,
                     "actual_keep_ratio": actual, "lookup_us": elapsed_us})

    out = Path("benchmarks/results.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    mean_us = statistics.mean(r["lookup_us"] for r in rows)
    accuracy = sum(r["expected_keep_ratio"] == r["actual_keep_ratio"] for r in rows) / len(rows)
    print(f"cases={len(rows)}")
    print(f"policy_accuracy={accuracy:.3f}")
    print(f"mean_lookup_us={mean_us:.3f}")
    print(f"results={out}")


if __name__ == "__main__":
    main()
