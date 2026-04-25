
# Emperor — Terminal Coding Assistant

Emperor is a terminal-based coding assistant that uses a tool-driven interface to explore, read, and modify code. Instead of directly generating answers, the system operates by calling structured tools that interact with the filesystem, allowing it to behave more like a real development agent than a text-only model.

The design is inspired by the idea that language models should not pretend to know everything about a system they cannot see. Instead, they should inspect their environment, gather information, and act based on actual state. This philosophy is discussed in the article “The Emperor Has No Clothes” by Mihail Eric, which motivates the use of tool-augmented reasoning over blind text generation.

![The Emperor Has No Clothes](./image.png)

## Features

Emperor provides a minimal but practical set of capabilities for interacting with a codebase through a language model. It can list directories, read files, and apply targeted edits. All actions are executed through explicit tool calls, ensuring that the model does not hallucinate file contents or structure.

The system enforces strict rules around tool usage. The model must explore before editing, operate on real data, and make minimal changes instead of rewriting entire files. This results in more predictable and controlled behavior compared to standard chat-based assistants.

## Architecture

```
emperor/
├── constants.py      # Terminal color configuration
├── file.py           # Path resolution utilities
├── main.py           # Core agent loop and tool execution
└── requirements.txt  # Dependencies
```

The system is built around a simple execution loop. A conversation is maintained between the user and the assistant, and each assistant response is parsed for tool calls. When a tool is invoked, it executes locally and returns structured output, which is then fed back into the model.

This loop continues until the model produces a final response without any tool calls.

## Core Components

The system revolves around three primary tools:

* `list` — Lists directory contents
* `read` — Reads file contents
* `write` — Creates or edits files with controlled replacement

Each tool operates on real filesystem paths and returns structured JSON responses. The write operation is intentionally constrained to prevent uncontrolled modifications by requiring the existing content to match before replacement.

## How It Works

1. The user enters a command in the terminal
2. The conversation is sent to the language model
3. The model either responds directly or issues a tool call
4. If a tool is called, it is executed locally
5. The result is appended to the conversation
6. The loop continues until the task is complete

Tool calls must follow a strict format:

```
tool: TOOL_NAME({"key": "value"})
```

Only one tool can be called at a time, and the model must wait for the result before proceeding.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Ensure Ollama is running with a model:

```bash
ollama run <model-name>
```

Create a `.env` file:

```env
OLLAMA_MODEL_NAME=<model-name>
```

Run the assistant:

```bash
python main.py
```

You will be prompted for a username and then enter an interactive session.

## Design Principles

Emperor follows a few strict principles:

* The model must not assume filesystem state
* All knowledge about files must come from tools
* Edits should be minimal and precise
* Errors should be handled by re-exploration, not guessing
* Execution should be transparent and reproducible

These constraints are what make the system reliable despite using a probabilistic model underneath.

## Inspiration

This project is inspired by the article: [Mihail Eric — The Emperor Has No Clothes](https://www.mihaileric.com/The-Emperor-Has-No-Clothes/). The article argues that language models often appear capable because they produce confident text, even when they lack grounding in reality. Emperor takes the opposite approach by forcing the model to interact with the real environment through tools, reducing hallucination and improving correctness.

## Limitations

The system operates directly on the local filesystem and does not include sandboxing, which means incorrect tool usage can modify real files. It also depends on the language model to follow tool-calling rules correctly.

Tool execution is sequential, and the system does not yet support planning multiple steps in advance.

## Future Work

Potential improvements include:

* Stronger validation of tool calls
* Sandboxed execution environment
* File diff visualization for edits
* Multi-step planning and tool chaining
* Better error recovery strategies

## Contributing

Contributions are welcome. You can fork the repository, make changes, and open a pull request. Keeping changes minimal and well-tested will help maintain the reliability of the system.
