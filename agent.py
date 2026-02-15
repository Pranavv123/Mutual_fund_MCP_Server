# agent/agent.py

import os
import asyncio
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
#from langchain.schema import SystemMessage

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from prompt import SYSTEM_PROMPT

from dotenv import load_dotenv

load_dotenv()


# ============
# MCP CLIENT
# ============

class MCPToolWrapper:
    def __init__(self):
        self.transport = StdioTransport(
            command="python",
            args=["mf_mcp_server.py"],
        )
        self.client = None

    async def connect(self):
        self.client = Client(transport=self.transport)
        await self.client.__aenter__()

    async def close(self):
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def search_schemes(self, scheme_name: str):
        result = await self.client.call_tool(
            "search_schemes_tool",
            {"scheme_name": scheme_name},
        )
        return result


mcp_wrapper = MCPToolWrapper()


# =========================
# Convert MCP tool → LC Tool
# =========================

async def search_schemes_tool(scheme_name: str):
    return await mcp_wrapper.search_schemes(scheme_name)


search_tool = StructuredTool.from_function(
    name="search_schemes",
    description="Search mutual fund schemes by name",
    coroutine=search_schemes_tool,
)


# ============
# LLM SETUP
# ============

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


# ============
# AGENT
# ============

async def get_agent():
    await mcp_wrapper.connect()

    agent = create_agent(
        model=llm,
        tools=[search_tool],
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
