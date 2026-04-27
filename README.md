# Emperor — Terminal Coding Assistant

Emperor is a terminal-based coding assistant that interacts with codebases through structured tool calls rather than free-form text generation. Instead of assuming knowledge about a project, it inspects the filesystem, gathers context, and performs actions grounded in real state.

This approach is inspired by the idea that language models should not hallucinate unseen environments, but instead operate as agents that observe and act. The philosophy aligns with Mihail Eric’s *“The Emperor Has No Clothes”*, which critiques ungrounded model behavior.

![The Emperor Has No Clothes](./image.png)

---

## Overview

Traditional coding assistants generate answers based on incomplete context. Emperor takes a different approach:

* It **does not assume** anything about your codebase
* It **explores before acting**
* It **operates through tools only**
* It **modifies files with strict constraints**

This makes behavior more predictable, debuggable, and closer to how a real developer works.

## Features

* Tool-driven interaction model (no blind generation)
* Filesystem awareness via real-time inspection
* Controlled file editing with verification
* Deterministic and reproducible execution loop
* Minimal and focused design

## Architecture

```
emperor/
├── constants.py      # Terminal color configuration
├── file.py           # Path resolution utilities
├── main.py           # Agent loop and tool execution
```

The system runs a continuous loop:

1. User provides input
2. Model responds (either text or tool call)
3. Tool executes locally
4. Result is appended to conversation
5. Loop continues until completion

## Tools

Emperor exposes three core tools:

### `list`

Lists directory contents.

```python
list_tool(path: str) -> Dict[str, Any]
```

### `read`

Reads file contents.

```python
read_tool(file: str) -> Dict[str, Any]
```

### `write`

Creates or edits files with strict replacement rules.

```python
write_tool(file: str, old_content: str, new_content: str) -> Dict[str, Any]
```

**Key constraint:**
Edits only succeed if `old_content` exists in the file. This prevents uncontrolled overwrites.

## Tool Call Format

All tool calls must follow this exact format:

```
tool: TOOL_NAME({"key": "value"})
```

Rules:

* Single line only
* Valid JSON with double quotes
* One tool call at a time
* Wait for tool result before next step

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run an Ollama model:

```bash
ollama run <model-name>
```

Run Emperor:

```bash
python main.py <model-name>
```

Example:

```bash
python main.py llama3
```

## Design Principles

* **No hallucination** — all knowledge comes from tools
* **Explore first** — never edit without reading
* **Minimal edits** — avoid full rewrites
* **Grounded execution** — operate on real state
* **Recover via observation** — not guessing

## Limitations

* No sandboxing — operates on real filesystem
* Sequential execution only
* Relies on model to follow tool protocol
* No long-horizon planning yet

## Future Work

* Tool call validation and schema enforcement
* Sandboxed execution environment
* Diff-based edit visualization
* Multi-step planning and tool chaining
* Improved failure recovery

## Inspiration

This project is grounded in a broader shift from passive language models to **tool-augmented, environment-aware agents**.

* **Mihail Eric — *The Emperor Has No Clothes***
  [https://www.mihaileric.com/The-Emperor-Has-No-Clothes/](https://www.mihaileric.com/The-Emperor-Has-No-Clothes/)
  Highlights how language models can appear capable despite lacking grounding. Their fluency often masks the absence of real interaction with the environment, leading to confident but unverifiable outputs. Emperor addresses this by forcing a strict separation between what the model knows and what it can verify. Instead of relying on internal guesses, it must explicitly observe state through tools, retrieve evidence from the filesystem, and base every action on that evidence. This shifts the model from a generative oracle to an interactive agent, where correctness emerges from grounded interaction rather than persuasive text.

## Contributing

Contributions are welcome. Keep changes minimal, focused, and well-tested to preserve system reliability.
