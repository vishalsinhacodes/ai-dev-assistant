from fastapi import APIRouter

from app.api.schemas import AgentRequest, AgentResponse
from app.agent.agent import run_single_turn

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    result = await run_single_turn(request.message)
    return AgentResponse(**result)