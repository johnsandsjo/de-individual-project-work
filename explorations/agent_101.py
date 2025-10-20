from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import random

load_dotenv()

#Agent 1a - simple with tool decorator
def plain_agent_dec():
    agent = Agent(
        model='google-gla:gemini-2.5-flash',
        instructions=( #use system_prompt here if I want to base this instrcutions on something
            'You are a agent that always reply with a number coming from your tools '
            'This numebr you should take as a year and say mention one of the biggest news that year'
        )
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
        model='google-gla:gemini-2.5-flash',
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
    
if __name__ == "__main__":
    #plain_agent_dec()
    #plain_agent()
    less_plain_agent()