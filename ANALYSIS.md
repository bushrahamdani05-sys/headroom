# Headroom Extension & Evaluation Analysis

## 1. Scope
This submission exercises Headroom's library compression API and adds a proof-of-concept **task-aware adaptive compression policy**. The motivation is that search and debugging have different information-retention requirements.

## 2. Features Exercised
- `headroom.compress()` and `CompressConfig` for deterministic library-side compression.
- Content-aware compression transforms for structured data, code, and text.
- The broader repository documents client, proxy, MCP, agent, cache, memory, and observability capabilities; this report focuses on the deterministic library path so the experiment does not require a paid model/API key.

## 3. Extension
### Gap
A single fixed compression target is not ideal for every task. Code search can tolerate more reduction than debugging, where stack traces and local context matter.

### Implementation
Added [`headroom/adaptive_policy.py`](headroom/adaptive_policy.py). `AdaptivePolicy` maps `{content_type, task_type}` to a validated keep ratio, supports runtime updates, and provides an isolated snapshot plus a process-wide accessor.

Example:

```python
from headroom.adaptive_policy import get_global_policy
from headroom import compress

policy = get_global_policy()
target = policy.get_level("code", "search")
result = compress(messages, target_ratio=target)
```

Tests in [`tests/test_adaptive_policy.py`](tests/test_adaptive_policy.py) cover defaults, updates, fallback behavior, validation, and the global accessor.

## 4. Evaluation
### Benchmark design
The requested evaluation distinguishes the extension's deterministic effect from model quality. A reproducible benchmark was added at [`benchmarks/adaptive_policy_benchmark.py`](benchmarks/adaptive_policy_benchmark.py).

It evaluates 120 fixed policy-selection cases: six workload classes (code/json/text × search/debug/summary where applicable), repeated 20 times. The baseline is the existing fixed-target approach; the adaptive system selects task-specific targets. The benchmark records exact target-selection accuracy and lookup latency in [`benchmarks/results.csv`](benchmarks/results.csv) when executed.

Run:

```bash
python benchmarks/adaptive_policy_benchmark.py
pytest -q tests/test_adaptive_policy.py
pytest -q
```

### What can and cannot be concluded
The deterministic benchmark can establish that the policy selects the configured target reliably and quantify its runtime overhead. It **cannot** establish improved LLM task success or answer quality. No model/API result is fabricated here. A full coding-agent evaluation should use a fixed coding agent and identical tasks/tool traces for baseline versus adaptive policy, then report task success, tokens, latency, and failures.

## 5. Results and limitations
The policy has six explicit defaults: code-search 0.50, code-debug 0.80, JSON-search 0.20, JSON-debug 0.70, text-summary 0.20, and text-debug 0.70. All values are constrained to `(0, 1]` and can be updated at runtime.

The benchmark is deliberately model-free and therefore suitable for reproducibility without external API credentials. Its limitation is that it measures the policy mechanism rather than downstream coding-agent quality. The next rigorous step is a 20+ task paired coding-agent run with confidence intervals.

## 6. Conclusion
The repository now contains a concrete extension, automated tests, and a reproducible quantitative benchmark harness. The extension changes policy selection without modifying Headroom's underlying compressors, keeping the proof of concept low-risk and easy to integrate.
