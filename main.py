# main.py
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

from agent import llm
from prompt import SYSTEM_PROMPT


class QueryRequest(BaseModel):
    query: str


# Shared state container
class AppState:
    agent = None
    session = None
    lock = asyncio.Lock()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    server_params = StdioServerParameters(
        command="python",
        args=["mf_mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await load_mcp_tools(session)

            AppState.agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
            )

            AppState.session = session

            print("✅ MCP + Agent initialized")

            yield   # 🚀 App runs here

            print("🛑 Shutting down MCP")


app = FastAPI(
    title="Mutual Fund Agent API",
    lifespan=lifespan
)


@app.post("/ask")
async def ask_agent(request: QueryRequest):

    try:
        async with AppState.lock:
            response = await AppState.agent.ainvoke(
                {"messages": [{"role": "user", "content": request.query}]}
            )

        final_message = response["messages"][-1].content

        return {"response": final_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))