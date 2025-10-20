import asyncio
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()

dbt_mcp_server = MCPServerStdio(
        command = "uvx",
        args= ["dbt-mcp"],
        cwd= os.getenv("DBT_PROJECT_DIR"), 
        env= {
            "DBT_PROJECT_DIR": os.getenv("DBT_PROJECT_DIR"),
            "DBT_PATH": os.getenv("DBT_PATH"), 
            "DBT_PROFILES_DIR": os.getenv("DBT_PROFILES_DIR"),
        }
        )

agent = Agent(
        model='google-gla:gemini-2.5-flash',
        instructions="You are an analytics Engineer, always answer which tools you have access to.",
        toolsets=[dbt_mcp_server]
)

async def main():
    async with agent:
        print("✅ dbt MCP Server successfully launched and connected via stdio.")
        
        result = await agent.run('What tools do you have access to Use a star emoji for every tool?')
    print(result.output)
        
# if __name__ == "__main__":
#     asyncio.run(main())