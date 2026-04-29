import os
import json
import re
from openai import AsyncOpenAI
from app.agent.tools import execute_tool

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = """You are an AI assistant for backend developers.
You have access to these tools:
1. web_search(query: str) - Search the web for general information
2. read_file(path: str) - Read contents of a local file
3. run_python(code: str) - Execute Python code and return the actual output
4. get_package_version(package: str) - Get latest version of any Python package from PyPI

You must follow the ReAct pattern strictly. Every response must be a JSON object with this structure:
For a tool call:
{
    "thought": "I need to... because...",
    "action": "tool_name",
    "input": {"param": "value"}
}

For a final answer:
{
    "thought": "I now have enough information to answer because...",
    "action": "final_answer",
    "input": {"answer": "your full answer here"}
}

STRICT RULES:
- ALWAYS include a "thought" field explaining your reasoning before acting
- For ANY question about latest package versions — use get_package_version
- For current info, news, recent events — use web_search
- For file contents — use read_file
- To run or verify code — use run_python
- If a tool returns an error or empty result — think about why and try a different approach
- One action per response
- Respond in JSON only, no extra text, no markdown"""

def extract_json(text: str):
    """Extract JSON from model response, handling markdown code blocks."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    text = text.replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object inside text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None

async def run_react_loop(user_message: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    steps = []
    max_iterations = 7
    
    for i in range(max_iterations):
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,  # type: ignore
            max_tokens=4096,
            temperature=0
        )
        
        raw = response.choices[0].message.content or ""
        print(f"\n--- Step {i+1} ---\n{raw}\n")
        
        parsed = extract_json(raw)
        
        if not parsed:
            return {
                "answer": raw,
                "steps": steps,
                "total_steps": len(steps),
                "success": False
            }
            
        thought = parsed.get("thought", "No thought provided")
        action = parsed.get("action", "")
        inputs = parsed.get("input", {})
        
        # Final answer reached
        if action == "final_answer":
            return {
                "answer": inputs.get("answer", raw),
                "steps": steps,
                "total_steps": len(steps),
                "success": True
            }
            
        # Execute the tool
        print(f"Thought: {thought}")
        print(f"Calling tool: {action} with {inputs}")
        
        observation = await execute_tool(action, inputs)
        print(f"Observation: {observation[:200]}")
        
        # Record this step
        steps.append({
            "step": i + 1,
            "thought": thought,
            "action": action,
            "action_input": inputs,
            "observation": observation
        })
        
        # Add to conversation history
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": f"Obervation: {observation}\n\nContinue."
        })
        
    return {
        "answer": "Max iterations reached without final answer.",
        "steps": steps,
        "total_steps": len(steps),
        "success": False
    }        

# --- Milestone 1 reference (single-turn, no reasoning trace) ---
# async def run_single_turn(user_message: str) -> dict:
#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": user_message}
#     ]

#     tool_calls_made = []
#     max_iterations = 5

#     for _ in range(max_iterations):
#         response = await client.chat.completions.create(
#             model=MODEL,
#             messages=messages,    # type:ignore
#             max_tokens=4096,
#             temperature=0  # deterministic output — critical for JSON parsing
#         )

#         raw = response.choices[0].message.content or ""
#         print(f"\nModel response:\n{raw}\n")

#         parsed = extract_json(raw)

#         if not parsed:
#             return {
#                 "answer": raw,
#                 "tool_calls": tool_calls_made,
#                 "turns": len(tool_calls_made) + 1
#             }

#         if "action" not in parsed:
#             return {
#                 "answer": raw,
#                 "tool_calls": tool_calls_made,
#                 "turns": len(tool_calls_made) + 1
#             }

#         action = parsed.get("action")
#         inputs = parsed.get("input", {})

#         if action == "final_answer":
#             return {
#                 "answer": inputs.get("answer", raw),
#                 "tool_calls": tool_calls_made,
#                 "turns": len(tool_calls_made) + 1
#             }

#         # It's a tool call
#         tool_result = await execute_tool(action, inputs)    # type:ignore
#         print(f"Tool '{action}' result: {tool_result[:200]}")

#         tool_calls_made.append({
#             "tool": action,
#             "input": inputs,
#             "result": tool_result
#         })

#         # Add tool call + result to conversation history
#         messages.append({"role": "assistant", "content": raw})
#         messages.append({
#             "role": "user",
#             "content": f"Tool result for {action}:\n{tool_result}\n\nNow continue."
#         })

#     return {
#         "answer": "Max iterations reached without final answer.",
#         "tool_calls": tool_calls_made,
#         "turns": max_iterations
#     }