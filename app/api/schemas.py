from pydantic import BaseModel
from typing import Any

class AgentRequest(BaseModel):
    message: str
    
class ToolCall(BaseModel):
    tool: str
    input: dict[str, Any]
    result: str
    
class AgentResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]
    turns: int