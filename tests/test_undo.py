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

navvy.undo_commit_changes() # Undo commit
print(navvy.get_all_commits()) # Show all commits made by Navvy