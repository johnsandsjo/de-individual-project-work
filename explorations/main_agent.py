import asyncio
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv() 

model_name = "gemini/gemini-2.5-flash"

async def run(mcp_server):
    agent = Agent(
        name="Analytics Enginer Assistant",
        instructions=f"You should answer questions about mart models in this dbt Core project. For this you will need to read the files using the mcp server tools.",
        mcp_servers=[mcp_server],
        model=LitellmModel(model=model_name)
    )

    message = "What is the names of the src models. Answer with a Python list?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "How many src tables does this relate to?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():

    async with MCPServerStdio(
        params = {
        "command":  "uvx", 
        "args": ["dbt-mcp"],
        "cwd": "/Users/john.sandsjo/Documents/github/de-individual-project-work/pipeline/data_transformation",
        "env": {
            "DBT_PROJECT_DIR":"/Users/john.sandsjo/Documents/github/de-individual-project-work/pipeline/data_transformation",
            "DBT_PROFILES_DIR": "/Users/john.sandsjo/.dbt",
            "DBT_PATH": "/Users/john.sandsjo/Documents/github/de-individual-project-work/.venv/bin/dbt", 
            }
        }
        ) as server:
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())