# agent/main.py

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

from agent import get_agent, mcp_wrapper

app = FastAPI(title="Mutual Fund Agent API")


class QueryRequest(BaseModel):
    query: str


@app.on_event("startup")
async def startup_event():
    global agent_instance
    agent_instance = await get_agent()


@app.on_event("shutdown")
async def shutdown_event():
    await mcp_wrapper.close()


@app.post("/ask")
async def ask_agent(request: QueryRequest):
    response = await agent_instance.ainvoke(
        {"messages": [{"role": "user", "content": request.query}]}
    )

    # LangChain 1.x returns messages list
    final_message = response["messages"][-1].content

    return {
        "response": final_message
    }

