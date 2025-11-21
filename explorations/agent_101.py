from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import random
import pandas as pd
from pathlib import Path
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()

#Agent 1a - simple with tool decorator
def plain_agent_dec():
    agent = Agent(
        model='google-gla:gemini-2.5-flash',
        instructions=( #use system_prompt here if I want to base this instrcutions on something
            'You are a agent that always reply with a number coming from your tools '
            'This numebr you should take as a year and mention one of the biggest news that year'
        ),
    )

    @agent.tool_plain
    def rand_year(): 
        #     """take the context and turn them into two ints. into a sum to return a sum"""
        return random.randint(2020, 2024)

    result = agent.run_sync()
    print(result.output)

#Agent 1b - tools keyword argument directly in agent instance
def rand_year(): 
    """take the context and turn them into two ints. into a sum to return a sum"""
    return random.randint(2000, 2020)

def plain_agent():
    agent = Agent(
        model='google-gla:gemini-2.0-flash',
        instructions=( 
            'You are a agent that always reply with a number coming from your tools '
            'This numebr you should take as a year and say mention one of the biggest news that year'
        ),
        tools=[rand_year]
    )

    result = agent.run_sync()
    print(result.output)

#Agent 2 - Use the user input
def less_plain_agent():
    agent = Agent(
        model='google-gla:gemini-2.5-flash',
        deps_type=str,
        instructions=( 
            'You are a agent that takes a year as input from the user'
            'This year you should mention one of the biggest news events that year'
        )
    )
    @agent.tool
    def getyear(ctx: RunContext[str]) -> str: 
        """Get the users year request"""
        return ctx.deps
    result = agent.run_sync(deps=input("Tell me a year "))
    print(result.output)


#Agent with a file as context
def read_data():
    data_path = Path(__file__).parents[1] / "data" / "scb_stats.csv"
    df = pd.read_csv(data_path, skiprows=2, encoding='latin-1')
    return df.head(10).to_string()

#def read_data_tool(ctx: RunContext[None] = None):
def agent_with_csv():
    agent = Agent(
        model='google-gla:gemini-2.5-flash',
        instructions=( 
            'You are a agent that takes a csv as input, you should then summarise it based on the user prompt'
        ),
        tools=[read_data]
    )
    result = agent.run_sync(user_prompt="Load the data using your tool and provide a 50-word summary.")
    print(result.output)

#Agent with a file + a return format
def read_data():
    data_path = Path(__file__).parents[1] / "data" / "scb_stats.csv"
    df = pd.read_csv(data_path, skiprows=2, encoding='latin-1')
    return df.head(10).to_string()

def agent_with_csv_to_sql():
    agent = Agent(
        model='google-gla:gemini-2.5-flash',
        instructions=( 
            """You are a SQL query generator.
            You take csv as input
            Your ONLY output must be a single, valid SQL statement to be used in dbt_modelling.
            It should inlcude all the columns from the csv and include CAST TO if the column should be transformed
            Include explanation in comments if you re cast any columns
            DO NOT include any backticks or other text.
            """
        ),
        tools=[read_data]
    )
    result = agent.run_sync(user_prompt="Load the data and return with the sql code that can be used in dbt modelling step")
    print(result.output)


#Agent to actually use mcp server
dbt_mcp_server = MCPServerStdio(
        'uv',
        args= ["run", "dbt-mcp", "stdio"],
        )

def agent_mcp():
    agent = Agent(
        model='google-gla:gemini-2.0-flash',
        instructions=( 
            """
            Using the dbt toolset, call the function to list all dbt nodes (models, sources, seeds)
            and return the resulting list of names.
            You must use the dbt toolset for this task.
            """
        ),
        toolsets=[dbt_mcp_server],
    )
    result = agent.run_sync()
    
    print(result.output)

if __name__ == "__main__":
    #plain_agent_dec()
    #plain_agent()
    #less_plain_agent()
    #agent_with_csv()
    agent_with_csv_to_sql()
    #agent_mcp()


    # def read_schema():
#     """Open the schema.yml file"""
#     path = Path(__file__).parents[1]/"pipeline/data_transformation/models"
#     open(f"{path}/schema.yml")

# def write_schema(content):
#     """Write operation to the file schema.yml"""
#     with open(f"../pipeline/data_transformation/models/schema.yml", "a") as f:
#         f.write(content)