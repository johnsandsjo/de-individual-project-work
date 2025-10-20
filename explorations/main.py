from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
import asyncio
#from dotenv import load_dotenv

#load_dotenv() 

model_name = "gemini/gemini-2.5-flash"

async def interactive_main():
    mcp_server =  MCPServerStdio(
    name="dbt_mcp_server",  #name for the server
    params = {
        "command":  "uvx", 
        "args": ["dbt-mcp"],
        "cwd": "/Users/john.sandsjo/Documents/github/de-individual-project-work/pipeline/data_transformation",
        "env": {
            "DBT_PROJECT_DIR":"/Users/john.sandsjo/Documents/github/de-individual-project-work/pipeline/data_transformation",
            "DBT_PATH": "/Users/john.sandsjo/Documents/github/de-individual-project-work/.venv/bin/dbt", 
            "DBT_PROFILES_DIR": "/Users/john.sandsjo/.dbt",
        }
    })
    async with mcp_server:
        analytics_agent = Agent(
            name="Analytics Engineer Agent",
            instructions="You are an analytics engineer whose job is to document data sources and write tests. You must use the tools available from the dbt_mcp_server to execute dbt commands.",
            mcp_servers=[mcp_server], 
            model=LitellmModel(model=model_name), 
            )

    # 4. Run the Agent
        result = await Runner.run(
            analytics_agent, 
            "I will list all source models."
        )
        print(f"Final Agent Output: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(interactive_main())