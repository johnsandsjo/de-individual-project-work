from pydantic_ai import Agent, RunUsage
from pydantic_ai.mcp import MCPServerStdio
from modelling import FilePrompt, DbtSourceYml, SqlFileContent
from connect_db import query_data_warehouse
from dotenv import load_dotenv
from pathlib import Path
import yaml

load_dotenv()
env_path = Path(__file__).parents[2]/".env"

src_models_path = Path(__file__).parents[1]/"data_transformation/models/source"

first_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=FilePrompt,
    system_prompt="""
    Make use of your tools to fetch data from a table mentioned in the prompt.
    Based on the columns of this table, create a prompt to another agent that will create one yml file.
    Include a suitable table name in prompt as well a brief description of what it includes.
    Convert the output of the tool into a string in your new prompt
    """,
    tools=[query_data_warehouse]
    )

def create_new_yml_file(yml_data : DbtSourceYml):
    """Accepts a validated Pydantic object and dumps it into a new yml file."""
    #from Pydantic object to standard Python dict
    data_dict = yml_data.model_dump(exclude_none=True,)

    #make it idempotent
    Path.mkdir(src_models_path, parents=True, exist_ok=True)

    with open(f"{src_models_path}/new_source.yml", 'w') as file:
        yaml.dump(data_dict, file, sort_keys=False, indent=2)

    return f"Successfully created dbt YAML file: new_source.yml"


# Second agent takes the result of the first agent
second_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=DbtSourceYml,
    system_prompt="""
    Based on the input data, generate a Python dictionary that conforms to the YAML structure in the output type. 
    The table name, table description and table identifier should be suited based on the input data.
    It MUST be a valid JSON/Dictionary.
    Finally you MUST call the tool: create_new_yml_file with the object as input.
    """,
    tools=[create_new_yml_file],
    retries=3
)

#third agent doing the same as agent one but with sql prompt
third_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=FilePrompt,
    system_prompt="""
    You will recieve a table name from the prompt in the format [schema_name].[table_name].
    Make use of the full name when using your tool to fetch data from a data warehouse.
    
    Based on the columns of this table, create a prompt to another agent that will create one sql file.
    
    CRITICAL NAMING RULE: The table name used in the subsequent prompt MUST be the [table_name] part 
    of the input (e.g., if the input is staging.scb_stats, use 'scb_stats'). DO NOT add any prefixes like 'stg_'.
    
    Include this non-prefixed table name in the new prompt, along with a brief description of what it includes.
    Convert the output of the tool into a string in your new prompt.
    """,
    tools=[query_data_warehouse]
    )

def create_new_sql_file(sql_data):
    """Create a new source as a sql file inside the models/source folder"""
    #makes it idempotent
    Path.mkdir(src_models_path, parents=True, exist_ok=True)
    with open(f"{src_models_path}/new_sql.sql", "w") as f:
        f.write(sql_data)

# Fourth agent takes the result of the third agent
fourth_agent = Agent(
    model="google-gla:gemini-2.0-flash",
    output_type=SqlFileContent,
    system_prompt="""
    Based on the input prompt, generate a valid SQL file.
    Use Jinja macros to fetch the source like '{{ source('dbt_agent', '[identifier]') }}'
    Column names should be taken from the prompts and be renamed and data types enforced.
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
            You are connected to the dbt Metadata and Control Plane (MCP) server. 
            Your primary directive is to execute dbt commands. 
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
    #staging.prj_daily_job_ads
    prompt_one = prompt_input

    result_one = await first_agent.run(
        prompt_one,
        usage=usage
    ) 
    
    first_agent_response = result_one.output

    print("\n" + "="*50)
    print(f"First agent's output:")
    print(f"{first_agent_response.prompt}")

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
    print(f"{result_three.output.prompt}")
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