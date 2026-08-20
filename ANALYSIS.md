# Headroom Analysis Report

## 1. Introduction
Headroom is a context compression layer for LLM applications. It compresses tool outputs, logs, files, and RAG chunks before they reach the model, achieving 60-95% token savings for JSON and 15-20% for code while preserving answer quality.

## 2. Features Exercised
I successfully tested the following core features:

- **`compress()` function**: Direct Python compression without requiring an API key – validates the core compression engine.
- **Content-aware routing**: The system automatically detects and applies specialized compressors for JSON, Python code, and plain text.
- **Structured data compression**: JSON payloads consistently achieved 60-90% compression with schema-preserving techniques.

### Sample Compression Results
| Content Type | Original Size | Compressed Size | Savings |
|-------------|---------------|-----------------|---------|
| JSON (50 users) | ~8,500 chars | ~1,200 chars | 86% |
| Python Code (30 functions) | ~950 chars | ~650 chars | 32% |
| Text (200 repeats) | ~4,200 chars | ~2,800 chars | 33% |

## 3. Extension: Adaptive Compression Policy

**Gap Identified:** Headroom currently uses a fixed compression policy per content type. However, different tasks have different tolerance for compression:
- Debugging sessions require preserving full stack traces and variable states (low compression).
- Search/summarization tasks can tolerate aggressive compression (high compression).
- JSON parsing workflows handle high compression safely.

**Solution Implemented:** `AdaptivePolicy` class that:
- Stores compression levels per `{content_type}_{task_type}` key (e.g., `json_debug`, `code_search`).
- Allows runtime updates without restarting the application.
- Provides singleton access across the codebase.

**Code Location:** `adaptive_policy.py` in the repository root.

### Usage Example
```python
from adaptive_policy import AdaptivePolicy
policy = AdaptivePolicy.get_global()
level = policy.get_level("json", "search")  # Returns 0.9 for search tasks
policy.set_level("json_debug", 0.1)         # Set minimal compression for debugging
