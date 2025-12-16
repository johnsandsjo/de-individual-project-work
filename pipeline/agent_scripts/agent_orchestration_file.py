from pydantic_ai import Agent, RunUsage
from pydantic_ai.mcp import MCPServerStdio
from pipeline.agent_scripts.data_models import YAMLPromptDetails, SRCfile, DbtSourceYml, SqlFileContent
from dotenv import load_dotenv
from pathlib import Path
from connect_db import query_data_warehouse
from agent_tools import create_new_yml_file, create_new_sql_file


load_dotenv()
env_path = Path(__file__).parents[2]/".env"

src_models_path = Path(__file__).parents[1]/"data_transformation/models/source"

first_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    system_prompt="""
    Your task is to analyze the column headers from the source data provided by the 'query_data_warehouse' tool.
    DO NOT return the raw data. Analyze the data to determine the column schema.
    Based on the column names, create a suitable table name, a brief description, and a list of all column names.
    Adhere strictly to the 'YAMLPromptDetails' Pydantic output format.
    """,
    output_type=YAMLPromptDetails,
    tools=[query_data_warehouse]
    )

# Second agent takes the result of the first agent
second_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=DbtSourceYml,
    system_prompt="""
    You have received a prompt detailing a database table schema (name, description, and columns).
    Your task is to generate a dbt schema documentation YAML file based on this input.
    The YAML content must be valid, correctly indented, and adhere strictly to the dbt documentation format.
    The file name should correspond to the model name in the prompt.
    Adhere strictly to the 'YMLFile' Pydantic output format.
    """,
    tools=[create_new_yml_file],
    retries=3
)

#third agent doing the same as agent one but with sql prompt
third_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=SRCfile,
    system_prompt="""
    You have recieved a table name from the prompt in the format [schema_name].[table_name].
    Make use of this full name then use your tool query_data_warehouse to fetch data from the data warehouse source.
    Your task is to prepare for a dbt source sql file based on this input to SELECT from the source.
    The SQL content must be valid and adhere strictly to the dbt documentation format.
    Adhere strictly to the 'SRCfile' Pydantic output format.
    """,
    tools=[query_data_warehouse]
    )

# Fourth agent takes the result of the third agent
fourth_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=SqlFileContent,
    system_prompt="""
    Based on the input prompt, generate a valid SQL file.
    Use Jinja macros to fetch the source like '{{ source('dbt_agent', '[identifier]') }}'
    Column names should be taken from the prompt and be renamed and data types enforced.
    Finally you MUST call the tool: create_new_sql_file.
    """,
    tools=[create_new_sql_file],
    retries=3
)

dbt_mcp_server = MCPServerStdio(
    'uv',
    args=["run", "--env-file", f"{env_path}", "dbt-mcp", "stdio"],
    timeout=60
)

mcp_agent = Agent(
        model='google-gla:gemini-2.0-flash',
        system_prompt=( 
            """
            Your primary directive is to execute dbt commands. 
            You are connected to the dbt MCP server.
            When asked to run tests without a specific selector, default to running all tests. 
            ACTION: Run 'dbt test --select *' via the mcp server tool.
            """
        ),
        toolsets=[dbt_mcp_server]
)


#Orchestration function
async def agentic_workflow():
    usage = RunUsage()
    
    # Execute 1st agent
    prompt_input = input("Give the name of the new source as provided in the warehouse ")
    print()
    prompt_one = prompt_input

    result_one = await first_agent.run(
        prompt_one,
        usage=usage
    ) 
    
    first_agent_response = result_one.output

    print("\n" + "="*50)
    print(f"First agent's output:")
    print(f"{first_agent_response}")

    #Human in the loop 1
    print()
    input("Press ENTER to approve this prompt and run second agent")
    print()

    # Prompt for second agent, using output from frist agent
    prompt_two = f"Act on this prompt: '{first_agent_response}'"
    print(f"\n-> Running second agent with new prompt: '{prompt_two}'")

    #Execute 2nd agent
    result_two = await second_agent.run(
        prompt_two,
        usage=usage
        )
    
    # Prompt for third agent, using output from second agent
    prompt_three = f"Act on this prompt: '{result_two.output}'"
    print(f"\n-> Running third agent with new prompt: '{prompt_input}'")

    #Execute 3rd agent
    result_three = await third_agent.run(
        prompt_three,
        usage=usage
        )
    print(f"Third agent's output:")
    print(f"{result_three.output}")
    print()
    input("Press ENTER to approve this prompt and run second agent")
    print()

    # Prompt for fourth agent, using output from third agent
    prompt_four = result_three.output.prompt
    print(f"\n-> Running fourth agent with new prompt: '{prompt_four}'")

    #Execute 4th agent
    result_four = await fourth_agent.run(
        prompt_four,
        usage=usage
        )

    final_result = result_four.output
    print("\n" + "="*50)
    print(f"Agent orchestartion ended ")
    print()

    print("Starting MCP agent")
    mcp_result = await mcp_agent.run()
    print("\n--- MCP agent response ---")
    print(mcp_result.output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(agentic_workflow())