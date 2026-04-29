from pydantic import BaseModel
from typing import Any

class AgentRequest(BaseModel):
    message: str
    
class ReActStep(BaseModel):
    step: int
    thought: str
    action: str
    action_input: dict[str, Any]
    observation: str    
    
class ToolCall(BaseModel):
    tool: str
    input: dict[str, Any]
    result: str
    
class AgentResponse(BaseModel):
    answer: str
    steps: list[ReActStep]
    total_steps: int
    success: bool