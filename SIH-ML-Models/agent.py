import json
import os
import subprocess
from pathlib import Path

from ollama import chat


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# Change this if `ollama list` shows a different Qwen model.
MODEL = "qwen3:8b"

MAX_ITERATIONS = 30

# Commands that should never be executed by the agent.
BLOCKED_COMMANDS = [
    "format ",
    "del /s",
    "rmdir /s",
    "rm -rf",
    "shutdown",
    "restart",
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a local autonomous ML coding agent.

You are working directly inside the user's project:

SIH-ML-Models

You have real tools for:
- listing files
- reading files
- searching files
- writing files
- executing terminal commands

IMPORTANT:

You are NOT a chatbot giving generic instructions.

When the user asks you to inspect or modify the project,
ACTUALLY USE THE TOOLS.

Never invent:
- files
- directories
- model names
- checkpoints
- accuracy
- experiment results
- training results

Only report information obtained from the tools.

============================================================
PROJECT RULES
============================================================

1. Work only inside the project directory.

2. Before modifying an existing file:
   READ IT FIRST.

3. Never delete files unless explicitly requested.

4. Never overwrite an existing model checkpoint.

5. Never modify .env files.

6. Never expose secrets.

7. Keep existing experiments intact.

8. When creating a new ML experiment, use a new filename.

9. Do not claim that a model improved accuracy unless it was
   actually trained and evaluated.

10. When comparing models, use the same evaluation protocol.

11. Do not use the test set to tune hyperparameters.

12. Use validation data for experiment decisions.

13. Test data should only be used for final evaluation.

============================================================
ML OBJECTIVE
============================================================

The long-term goal is to find the best-performing model
for this project.

Before creating a new model:

1. Inspect the existing project.
2. Find the current model architecture.
3. Find training scripts.
4. Find evaluation scripts.
5. Find preprocessing.
6. Find augmentation.
7. Find checkpoints.
8. Find actual experiment results.
9. Determine the current best model.

Only after understanding the baseline should you design
a new experiment.

============================================================
OFFLINE RULE
============================================================

This environment is completely offline.

DO NOT:

- use OpenAI
- use NVIDIA APIs
- use cloud APIs
- call external websites
- download models
- install packages automatically
- use internet-based services

Use only:

- local files
- local Python
- local terminal
- locally installed packages
- locally available Ollama models

If pretrained weights are unavailable locally,
report that instead of downloading them.

============================================================
TOOL USAGE
============================================================

Use list_files before exploring an unfamiliar directory.

Use read_file before modifying an existing file.

Use search_files when looking for:
- model names
- checkpoint paths
- accuracy
- training functions
- evaluation functions

Use run_command for:
- Python scripts
- tests
- evaluation
- training
- syntax checks
- git status

Use write_file only when an actual file change is required.

============================================================
EXPERIMENT MANAGEMENT
============================================================

Never overwrite the current best checkpoint.

For example:

models/
    best_existing.pth
    efficientnet_b3_exp7.pth

Create separate experiment directories where appropriate.

Record:
- model
- configuration
- metrics
- checkpoint
- experiment name

============================================================
BEHAVIOR
============================================================

Do not stop after saying:

"I cannot access your files."

You DO have file tools.

Use them.

Do not give hypothetical examples.

Inspect the actual project.

If a command fails:

1. Read the error.
2. Diagnose it.
3. Fix the relevant code.
4. Retry.
5. Report what happened.

============================================================
FINAL RESPONSE
============================================================

After completing a task, summarize:

FILES INSPECTED:
...

FILES CREATED:
...

FILES MODIFIED:
...

COMMANDS EXECUTED:
...

RESULTS:
...

CURRENT BEST MODEL:
...

EVIDENCE:
...

Never fabricate missing information.
"""


# ============================================================
# PATH SECURITY
# ============================================================

def safe_path(path):
    """
    Convert a project-relative path into a safe absolute path.
    """

    path = Path(path)

    if path.is_absolute():
        target = path.resolve()
    else:
        target = (PROJECT_ROOT / path).resolve()

    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError(
            f"Access denied: {path}"
        )

    return target


# ============================================================
# LIST FILES
# ============================================================

def list_files(path="."):
    try:
        directory = safe_path(path)

        if not directory.exists():
            return f"Directory does not exist: {path}"

        if not directory.is_dir():
            return f"Not a directory: {path}"

        ignored = {
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
        }

        output = []

        for item in sorted(directory.rglob("*")):

            if any(part in ignored for part in item.parts):
                continue

            relative = item.relative_to(PROJECT_ROOT)

            if item.is_dir():
                output.append(f"[DIR]  {relative}")
            else:
                output.append(f"[FILE] {relative}")

        if not output:
            return "Directory is empty."

        return "\n".join(output[:2000])

    except Exception as e:
        return f"LIST FILES ERROR: {e}"


# ============================================================
# READ FILE
# ============================================================

def read_file(path):
    try:
        file_path = safe_path(path)

        if not file_path.exists():
            return f"File does not exist: {path}"

        if not file_path.is_file():
            return f"Not a file: {path}"

        max_size = 2 * 1024 * 1024

        if file_path.stat().st_size > max_size:
            return (
                f"File is too large to read completely.\n"
                f"Path: {path}\n"
                f"Size: {file_path.stat().st_size} bytes"
            )

        content = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        return (
            f"===== FILE: {path} =====\n"
            f"{content}"
        )

    except Exception as e:
        return f"READ FILE ERROR: {e}"


# ============================================================
# SEARCH FILES
# ============================================================

def search_files(query):
    try:

        results = []

        ignored = {
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
        }

        for file_path in PROJECT_ROOT.rglob("*"):

            if not file_path.is_file():
                continue

            if any(part in ignored for part in file_path.parts):
                continue

            try:
                text = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except Exception:
                continue

            if query.lower() in text.lower():

                relative = file_path.relative_to(PROJECT_ROOT)

                results.append(
                    str(relative)
                )

        if not results:
            return f"No files found containing: {query}"

        return (
            f"Files containing '{query}':\n"
            + "\n".join(results[:500])
        )

    except Exception as e:
        return f"SEARCH ERROR: {e}"


# ============================================================
# WRITE FILE
# ============================================================

def write_file(path, content):
    try:

        file_path = safe_path(path)

        # Never modify environment files.
        if file_path.name.lower() == ".env":
            return "ERROR: Modifying .env is forbidden."

        existed = file_path.exists()

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        if existed:
            return f"Successfully modified: {path}"

        return f"Successfully created: {path}"

    except Exception as e:
        return f"WRITE FILE ERROR: {e}"


# ============================================================
# RUN COMMAND
# ============================================================

def run_command(command):

    lower = command.lower()

    for blocked in BLOCKED_COMMANDS:

        if blocked in lower:
            return (
                f"COMMAND BLOCKED for safety:\n"
                f"{command}"
            )

    try:

        print()
        print("=" * 70)
        print("EXECUTING")
        print("=" * 70)
        print(command)

        result = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            shell=True,
            capture_output=True,
            text=True,
            timeout=900
        )

        output = ""

        if result.stdout:
            output += "\n--- STDOUT ---\n"
            output += result.stdout

        if result.stderr:
            output += "\n--- STDERR ---\n"
            output += result.stderr

        output += (
            f"\n--- EXIT CODE: "
            f"{result.returncode} ---"
        )

        # Prevent gigantic tool responses.
        if len(output) > 30000:
            output = output[:30000]
            output += "\n[OUTPUT TRUNCATED]"

        return output

    except subprocess.TimeoutExpired:
        return (
            "COMMAND TIMEOUT: "
            "The command exceeded 900 seconds."
        )

    except Exception as e:
        return f"COMMAND ERROR: {e}"


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List actual files and directories in the "
                "local project."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Project-relative directory. "
                            "Use '.' for root."
                        )
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read an actual project file. "
                "Must be used before modifying an existing file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Project-relative file path."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": (
                "Search the contents of project files "
                "for a specific text string."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Text to search for."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or modify a project file. "
                "Never modify .env."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Project-relative file path."
                        )
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "Complete file contents."
                        )
                    }
                },
                "required": [
                    "path",
                    "content"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Execute a Windows terminal command "
                "from the project root."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Command to execute."
                        )
                    }
                },
                "required": ["command"]
            }
        }
    }
]


# ============================================================
# TOOL DISPATCH
# ============================================================

def execute_tool(name, arguments):

    if name == "list_files":
        return list_files(
            arguments.get("path", ".")
        )

    if name == "read_file":
        return read_file(
            arguments["path"]
        )

    if name == "search_files":
        return search_files(
            arguments["query"]
        )

    if name == "write_file":
        return write_file(
            arguments["path"],
            arguments["content"]
        )

    if name == "run_command":
        return run_command(
            arguments["command"]
        )

    return f"Unknown tool: {name}"


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent(user_request):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    for iteration in range(MAX_ITERATIONS):

        print()
        print("=" * 70)
        print(f"AGENT ITERATION {iteration + 1}")
        print("=" * 70)

        try:

            response = chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                options={
                    "temperature": 0.2
                }
            )

        except Exception as e:

            print()
            print("=" * 70)
            print("OLLAMA ERROR")
            print("=" * 70)
            print(e)

            return

        message = response["message"]

        messages.append(message)

        tool_calls = message.get("tool_calls")

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        if not tool_calls:

            print()
            print("=" * 70)
            print("QWEN")
            print("=" * 70)

            print(
                message.get(
                    "content",
                    ""
                )
            )

            return

        # ----------------------------------------------------
        # EXECUTE TOOLS
        # ----------------------------------------------------

        for tool_call in tool_calls:

            function = tool_call["function"]

            name = function["name"]

            arguments = function.get(
                "arguments",
                {}
            )

            print()
            print("TOOL:", name)
            print("ARGS:", arguments)

            try:

                result = execute_tool(
                    name,
                    arguments
                )

            except Exception as e:

                result = (
                    f"TOOL EXECUTION ERROR: {e}"
                )

            print()
            print("TOOL RESULT:")
            print(result[:5000])

            messages.append(
                {
                    "role": "tool",
                    "content": result
                }
            )

    print()
    print(
        "Agent stopped: maximum iterations reached."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LOCAL QWEN ML CODING AGENT")
    print("=" * 70)

    print(
        f"Model : {MODEL}"
    )

    print(
        f"Root  : {PROJECT_ROOT}"
    )

    print(
        "Mode  : OFFLINE"
    )

    print("=" * 70)

    print()
    print(
        "Qwen has access to:"
    )

    print(
        "  [1] list_files"
    )

    print(
        "  [2] read_file"
    )

    print(
        "  [3] search_files"
    )

    print(
        "  [4] write_file"
    )

    print(
        "  [5] run_command"
    )

    print()
    print(
        "Type 'exit' to stop."
    )
    print()

    while True:

        try:

            user_input = input(
                "You > "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\nExiting..."
            )

            break

        except EOFError:

            break

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit"
        }:
            break

        run_agent(
            user_input
        )


if __name__ == "__main__":
    main()