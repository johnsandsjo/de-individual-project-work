from pydantic_ai import Agent, RunUsage
from pydantic_ai.mcp import MCPServerStdio
from pipeline.agent_scripts.data_models import YAMLPromptDetails, SRCfile, DbtSourceYml, SqlFileContent
from dotenv import load_dotenv
from pathlib import Path
from pipeline.agent_scripts.connect_db import query_data_warehouse
from pipeline.agent_scripts.agent_tools import create_new_yml_file, create_new_sql_file
import time

load_dotenv()
env_path = Path(__file__).parents[2]/".env"
src_models_path = Path(__file__).parents[1]/"data_transformation/models/source"
llm_model = "google-gla:gemini-2.0-flash"

first_agent = Agent(
    model=llm_model,
    system_prompt="""
    Your task is to analyze the column headers from the raw data provided by the 'query_data_warehouse' tool.
    Analyze the data to determine the column schema and return the raw data. 
    Based on the column names, create a suitable table name, a brief description, and a list of all column names.
    Adhere strictly to the 'YAMLPromptDetails' Pydantic output format.
    """,
    output_type=YAMLPromptDetails,
    tools=[query_data_warehouse]
    )

# Second agent takes the result of the first agent
second_agent = Agent(
    model=llm_model,
    system_prompt="""
    You have received a prompt detailing a database table schema (name, description, and columns).
    Your task is to generate a dbt schema documentation YAML file based on this input.
    The YAML content must be valid, correctly indented, and adhere strictly to the dbt documentation format.
    The file name should correspond to the model name in the prompt.
    Adhere strictly to the 'DbtSourceYml' Pydantic output format.
    """,
    output_type=DbtSourceYml,
    tools=[create_new_yml_file],
    retries=3
)

#third agent doing the same as agent one but with sql prompt
third_agent = Agent(
    model=llm_model,
    output_type=SRCfile,
    system_prompt="""
    You have recieved a table name from the prompt in the format [table_name].
    Make use of this name then use your tool query_data_warehouse to fetch data from the data warehouse.
    Your task is to prepare for a dbt model sql file based on this input to SELECT from the source.
    The SQL content must be valid and adhere strictly to the dbt documentation format.
    Adhere strictly to the 'SRCfile' Pydantic output format.
    """,
    tools=[query_data_warehouse]
    )

# Fourth agent takes the result of the third agent
fourth_agent = Agent(
    model=llm_model,
    output_type=SqlFileContent,
    system_prompt="""
    You are a dbt developer. You will receive a schema definition.
    TASKS:
    1. Generate a SQL model using Jinja: {{ source('dbt_agent', 'identifier') }}.
    2. Keep the source column names, but tranlsate them to English (e.g. kön as `gender`)
    3. Make sure the columns data types are enforced.
    4. MANDATORY: Call the 'create_new_sql_file' tool with the generated SQL and the correct file name.
    5. After the tool confirms success, return the structured 'SqlFileContent' confirming what you did.
    """,
    tools=[create_new_sql_file],
    retries=3
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
    print("1st agent's comleted with prompt:\n")
    prompt_two = f"{first_agent_response}"
    print(f"{prompt_two}\n")

    #Human in the loop 1
    print()
    input("Press ENTER to approve this prompt and run 2nd agent\n")
    print(f"\n-> Running 2nd agent with prompt from agent 1")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")

    #Executing 2nd agent with prompt fro agent 1
    result_two = await second_agent.run(
        prompt_two,
        usage=usage
        )
    
    print("\n" + "="*50)
    print("Agent 2 is ready, new source YML file created\n")

    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".\n")

    # Prompt for third agent, using output from second agent
    prompt_three = f"Table name: '{prompt_one}'"
    print(f"\n-> Running 3rd agent with prompt:\n")
    print(f"{prompt_three}")

    #Execute 3rd agent
    result_three = await third_agent.run(
        prompt_three,
        usage=usage
        )
    
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".\n")
    
    print("\n" + "="*50)
    print(f"3rd agent's done, prompt for agent 4:")
    # Prompt for fourth agent, using output from third agent
    prompt_four = f"Create the SQL model for this schema: {result_three.output.model_dump_json()}"
    
    print(f"{prompt_four}\n")
    
    #Human in the loop 2
    input("Press ENTER to approve this prompt and run 4th agent\n")
    print(f"\n-> Running 4th agent with prompt from agent 3")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")

    #Execute 4th agent
    result_four = await fourth_agent.run(
        prompt_four,
        usage=usage
        )
    print("\n" + "="*50)
    print("Agent 4 is ready, new source SQL file created\n")

    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".\n")

    dbt_mcp_server = MCPServerStdio(
        'uv',
        args=["run", "--env-file", f"{env_path}", "dbt-mcp", "stdio"],
        timeout=120
    )
    
    print("Starting MCP Agent\n")
    #wrapping the part using MCP in an 'async with' block
    async with dbt_mcp_server as conn:
        mcp_agent = Agent(
            model=llm_model,
            system_prompt="""
            Execute dbt commands using the connected MCP server.
            If a command fails, explain why and ask the user for instructions.
            If the user provides a fix (like '--full-refresh'), execute it immediately.
            """,
            toolsets=[conn]
        )
        current_prompt = "Run dbt run"
        chat_history = [] 
        while True:
            print(f"\n[Agent]: Acting on -> {current_prompt}")
            # Pass chat_history
            result = await mcp_agent.run(current_prompt, message_history=chat_history)
            #Update history for agent's awareness
            chat_history = result.all_messages()
            
            print("\nMCP agent response")
            print(result.output)
            # Ask for user input to keep the loop going
            user_feedback = input("\nType your response (or 'exit' to finish): ")
            if user_feedback.lower() in ['exit']:
                break
            current_prompt = user_feedback


    print("\n" + "="*50)
    print(f"Agent orchestartion ended ")
    print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(agentic_workflow())