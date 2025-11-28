import asyncio
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

load_dotenv()
os.environ["DISABLE_REMOTE"] = "True"

env_path = Path(__file__).parents[2]/".env"

def write_data(file_name, content):
    """ Write the data to a new sql file inside the models folder"""
    with open(f"../pipeline/data_transformation/models/src/{file_name}", "a") as f:
        f.write(content)


dbt_mcp_server = MCPServerStdio(
    'uv',
    args=["run", "--env-file", f"{env_path}", "dbt-mcp", "stdio"],
    timeout=60
)

agent = Agent(
        model='google-gla:gemini-2.0-flash',
        instructions=( 
            """
            You are a helpful agent to help with my dbt project. Make use of the dbt mcp server
            """
        ),
        toolsets=[dbt_mcp_server]
)


async def main():
    print("Launching MCP Server via stdio.")
    result = await agent.run("Hello!")
    while True:
        print(f"\n{result.output}")
        user_input = input("\n")
        result = await agent.run(user_prompt=user_input, message_history=result.new_messages())

        
if __name__ == "__main__":
    asyncio.run(main())