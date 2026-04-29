from fastapi import APIRouter

from app.api.schemas import AgentRequest, AgentResponse, ReActStep
from app.agent.agent import run_react_loop

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    result = await run_react_loop(request.message)
    result["steps"] = [ReActStep(**s) for s in result["steps"]]
    # result = await run_single_turn(request.message)
    return AgentResponse(**result)