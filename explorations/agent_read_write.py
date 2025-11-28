import asyncio
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pathlib import Path
import pandas as pd

load_dotenv()
os.environ["DISABLE_REMOTE"] = "True"


def read_data():
    data_path = Path(__file__).parents[1] / "data" / "scb_stats.csv"
    df = pd.read_csv(data_path, skiprows=2, encoding='latin-1')
    return df.head(10).to_string()

def write_data(file_name, content):
    """ Write the data to a new sql file inside the models folder"""
    with open(f"../pipeline/data_transformation/models/src/{file_name}", "w") as f:
        f.write(content)



env_path = Path(__file__).parents[1]/".env"

dbt_mcp_server = MCPServerStdio(
    'uv',
    args=["run", "--env-file", f"{env_path}", "dbt-mcp", "stdio"],
    env={
        **os.environ,
    },
    timeout=60
)


agent = Agent(
        model='google-gla:gemini-2.0-flash',
        instructions=( 
            """
            Using the available dbt toolset, retrieve and return the names of all the dbt mart models.
            Specifically, call the dbt function to list nodes using the selector 'tag:mart'.
            You must use the dbt toolset for this task.
            """
        ),
        toolsets=[dbt_mcp_server], 
)

async def main():
    print("✅ dbt MCP Server successfully launched and connected via stdio.")
    result = await agent.run()

    print("\n--- Agent Response ---")
    print(result.output)
        
if __name__ == "__main__":
    asyncio.run(main())


# """You are a SQL query generator.
#             You take csv as input using the read_data() tool
#             Your final job is to create a single, valid SQL statement and write this data into a new file using write_data() tool
#             The sql should inlcude all the columns from the csv and include CAST TO if the column should be transformed
#             Include explanation in comments if you cast any columns
#             DO NOT include any backticks or other text.
#             When callin gthe write_data, you should send in a good file name with no extension and you should send in the sql script as string
#             """