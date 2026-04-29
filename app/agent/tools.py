import httpx
import subprocess

from ddgs import DDGS
from groq.types.chat import ChatCompletionToolParam

TOOL_DEFINITIONS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current information. Use this when you need "
                "up-to-date docs, error explanations, or library information."
            ),
            "parameters":{
                "type": "object",
                "properties":{
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a local file. Use this when the user asks "
                "about code in a specific file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute a small Python snippet and return stdout. Use for "
                "calculations, data transformations, or verifying logic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_package_version",
            "description": "Get the latest vesion of any Python package from PyPI. Use this for any question about the latest version of a Python library.",
            "parameters": {
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "The PyPI package name e.g. fastapi, django, pydantic"
                    }
                },
                "required": ["package"]
            }
        }
    }
]

async def execute_tool(name: str, inputs: dict) -> str:
    if name == "web_search":
        return await _web_search(inputs["query"])
    elif name == "read_file":
        return _read_file(inputs["path"])
    elif name == "run_python":
        return _run_python(inputs["code"])
    elif name == "get_package_version":
        return await _get_package_version(inputs["package"])
    else:
        return f"Error: unknown tool '{name}'"
    
from ddgs import DDGS

async def _web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        
        if not results:
            return "No results found."
        
        output = []
        for r in results:
            output.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}")
        
        return "\n\n".join(output)
    except Exception as e:
        return f"Search error: {e}"
        
def _read_file(path: str) -> str:
    try:
        if".." in path or path.startswith("/"):
            return "Error: path not allowed"
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > 4000:
                content = content[:4000] + "\n... (truncated)"
            return content
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Read error: {e}"
    
def _run_python(code: str) -> str:
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout or result.stderr or "(no output)"
        return output[:2000]
    except subprocess.TimeoutExpired:
        return "Error: code execution timed out"
    except Exception as e:
        return f"Execution error: {e}"
    
async def _get_package_version(package: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=10.0
            )
            data = resp.json()
            version = data["info"]["version"]
            return f"Latest version of {package}: {version}"
    except Exception as e:
        return f"Error fetching version: {e}"