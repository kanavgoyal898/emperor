import os
import json
import inspect

import ollama

from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, List, Tuple

from file import resolve_absolute_path

load_dotenv()

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
You are a coding assistant whose goal it is to help us solve coding tasks. 
You have access to a series of tools you can execute. Here are the tools you can execute:

{tools_description}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
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

OLLAMA_MODEL_NAME = "codellama"

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
