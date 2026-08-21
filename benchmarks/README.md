# Adaptive-policy benchmark

Run from the repository root:

```bash
python benchmarks/adaptive_policy_benchmark.py
```

The benchmark evaluates 120 fixed coding-agent workload-policy cases (20
repetitions of six workload classes). It reports exact policy-selection
accuracy and lookup latency and writes `benchmarks/results.csv`.

This is intentionally model-free: it measures the extension itself and does
not claim an LLM task-success improvement without a model/API run. The same
workload matrix can be paired with a coding agent for the full agent-level
evaluation requested by the assignment.
