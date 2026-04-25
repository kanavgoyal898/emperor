import os
import json
import time
import inspect

import ollama

from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict, List, Tuple

from constants import *
from file import resolve_absolute_path

load_dotenv()

OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME")

def read_tool(file: str) -> Dict[str, Any]:
    """
        Reads the content of a file and returns it as a string.
        If the file does not exist, returns an error message.

        Example:
        read_tool("file.txt") -> {"path": "/absolute/path/to/file.txt", "content": "This is the content of the file."}
    """

    path = resolve_absolute_path(file)
    print(f"Reading file: {path}")

    if not path.is_file():
        return {
            "path": str(path),
            "error": "File does not exist."
        }
    else:
        with open(str(path), "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "path": str(path),
            "content": content
        }
    
def list_tool(path: str) -> Dict[str, Any]:
    """
        Lists the contents of a directory. 
        If the path is not a directory, returns an error message.

        Example:
        list_tool("/path/to/directory") -> {"path": "/absolute/path/to/directory", "contents": [{"item": "file_name.txt", "type": "file"}, {"item": "directory_name", "type": "directory"}]}
    """

    path = resolve_absolute_path(path)
    print(f"Listing directory: {path}")

    if not path.is_dir():
        return {
            "path": str(path),
            "error": "Not a directory."
        }
    else:
        contents = [{"item": str(item.name), "type": "file" if item.is_file() else "directory"} for item in path.iterdir()]
        return {
            "path": str(path),
            "contents": contents
        }

def write_tool(file: str, old_content: str, new_content: str) -> Dict[str, Any]:
    """
        Writes new content to a file, replacing old content if it exists.
        If the file does not exist, it is created with the new content.
        If the old content is not found in the file, returns an error message.
        
        Example:
        write_tool("file.txt", "", "new content.") -> {"path": "/absolute/path/to/file.txt", "action": "File created."}
        write_tool("file.txt", "old content", "new content") -> {"path": "/absolute/path/to/file.txt", "action": "File edited."}
    """

    path = resolve_absolute_path(file)
    print(f"Writing file: {path}")

    if not old_content:
        path.write_text(new_content, encoding="utf-8")
        return {
            "path": str(path),
            "action": "File created."
        }
    else:
        if not path.is_file():
            return {
                "path": str(path),
                "error": "File does not exist."
            }
        else:
            old_file_content = path.read_text(encoding="utf-8")
            if old_file_content.find(old_content) == -1:
                return {
                    "path": str(path),
                    "error": "`old_content` not found in file."
                }
            else:
                new_file_content = old_file_content.replace(old_content, new_content, 1)
                path.write_text(new_file_content, encoding="utf-8")
                return {
                    "path": str(path),
                    "action": "File edited."
                }
            
TOOL_REGISTRY = {
    "read": read_tool,
    "list": list_tool,
    "write": write_tool
}

def get_tool_signature(tool_name: str) -> str:
    tool_func = TOOL_REGISTRY.get(tool_name)
    return f"""
    Name: {tool_name}
    Description: {tool_func.__doc__.strip()}
    Signature: {inspect.signature(tool_func)}
    """

SYSTEM_PROMPT = """
You are Emperor, an expert coding assistant running in a terminal environment.
Your job is to help users navigate, read, and modify code and files using the tools available to you.

## Available Tools
{tools_description}

## Tool Usage Rules
- To call a tool, output EXACTLY one line in this format and nothing else:
  tool: TOOL_NAME({{"key": "value"}})
- Use compact single-line JSON with double quotes only.
- Call ONE tool at a time. Wait for the tool_result before proceeding.
- After receiving a tool_result(...), analyze the result and continue the task.
- Never guess file contents or directory structures — use tools to explore first.
- If a tool returns an error, try to recover (e.g. check the path, list the directory).

## Behavior Guidelines
- Always explore before editing: list directories, read files before writing.
- When editing, make minimal, targeted changes. Do not rewrite entire files unless asked.
- Think step by step, but only output tool calls or final answers — no commentary mid-task.
- If a task is ambiguous, ask ONE clarifying question before proceeding.
- When the task is complete, give a short summary of what was done.

## Response Format
- Tool call → one line: tool: TOOL_NAME({{"key": "value"}})
- Final answer → plain text, concise, no markdown unless showing code
- Never mix a tool call with explanation in the same response.
"""

def get_system_prompt() -> str:
    tools_description = ""
    for i, (tool_name, _) in enumerate(TOOL_REGISTRY.items()):
        tools_description += f"Tool {i+1}:\n" + get_tool_signature(tool_name)
        tools_description += f"{'='*8}" + "\n\n\n"
    return SYSTEM_PROMPT.format(tools_description=tools_description)

def extract_tool_calls(message: str) -> List[Tuple[str, Dict[str, Any]]]:
    calls = []
    for line in message.splitlines():
        line = line.strip()
        if line.startswith("tool:"):
            try:
                tool_call = line[len("tool:"):].strip()
                tool_name, json_args = tool_call.split("(", 1)
                tool_name = tool_name.strip()
                if json_args.endswith(")"):
                    json_args = json_args[:-1].strip()
                    args = json.loads(json_args)
                    calls.append((tool_name, args))
            except Exception:
                continue

    return calls

def execute_llm_call(conversation: List[Dict[str, str]]) -> str:
    # content = ""

    # messages = []
    # for message in conversation:
    #     if message["role"] == "system":
    #         content = message["content"]
    #     else:
    #         messages.append(message)

    response = ollama.chat(
        model=OLLAMA_MODEL_NAME,
        messages=conversation
    )

    return response.get("message", {}).get("content", "")

def main():
    print("Initializing Emperor...")
    time.sleep(0.6)

    username = input("Username: ")
    print("Setting up environment...")
    time.sleep(1.2)

    print("Loading tools...")
    time.sleep(1.8)

    system_prompt = get_system_prompt()
    print("System prompt:\n", system_prompt)
    time.sleep(2.4)

    conversation = [{
        "role": "system",
        "content": system_prompt
    }]

    while True:
        try:
            user_content = input(f"{COLOR_USER}{username}:{COLOR_SYSTEM} ")
        except KeyboardInterrupt:
            break
        
        conversation.append({
            "role": "user",
            "content": user_content
        })

        while True:
            assistant_response = execute_llm_call(conversation)
            tool_calls = extract_tool_calls(assistant_response)

            conversation.append({
                "role": "assistant",
                "content": assistant_response
            })

            if not tool_calls:
                print(f"{COLOR_ASSISTANT}{OLLAMA_MODEL_NAME}:{COLOR_SYSTEM} {assistant_response}")
                break
            else:
                for tool_name, args in tool_calls:
                    tool = TOOL_REGISTRY.get(tool_name)
                    if not tool:
                        response = {"error": f"Unknown tool: {tool_name}"}
                    else:
                        response = tool(**args)

                    conversation.append({
                        "role": "user",
                        "content": f"tool_result: {json.dumps({"tool": tool_name, "response": response})}"
                    })

if __name__ == "__main__":
    main()
