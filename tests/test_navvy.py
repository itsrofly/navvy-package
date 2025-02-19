from navvy import Navvy
from pydantic_ai import Agent

# Create an agent using pydantic_ai
agent = Agent(  
    'openai:gpt-4o-mini',
    system_prompt=(
        'You are a software engineer working on a project. You have made some changes to the codebase and committed them. '
    ),
)
# Create a Navvy instance
navvy = Navvy(agent, "./snake_game")

# Run the agent
result = agent.run_sync("Create a snake game.")

print(result.data) # Agent response
print(navvy.get_all_commits()) # Show all commits made by Navvy