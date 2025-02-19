# Navvy

The navvy package is a Python-based automation tool for managing Git repositories. It utilizes the [PydanticAI](https://ai.pydantic.dev/) framework, enabling compatibility with any provider or model while maintaining structure and most of the wording. It facilitates tasks like evaluating, editing, creating, and deleting files within a repository.

## Installation

You can install the Navvy package using pip:

```sh
pip install navvy
```

## Usage

```python
from navvy import Navvy
from pydantic_ai import Agent

# Create an agent using pydantic_ai, accordance with the user's preferences.
agent = Agent(  
    'openai:gpt-4o-mini',
    system_prompt=(
        'You are a software engineer working on a project. You have made some changes to the codebase and committed them. '
    ),
)
# Create a Navvy instance
navvy = Navvy(agent, "./snake_game")

# Run the agent, accordance with the user's preferences.
result = agent.run_sync("Create a snake game.")

print(result.data) # Agent response
print(navvy.get_all_commits()) # Show all commits made by Navvy
```

Here is an example of how to undo a commit using the Navvy package:

```python
# Undo the last commit
navvy.undo_commit_changes()

# Undo the last commit using commit id
commit_id: str
navvy.undo_commit_changes(commit_id)
```

## API 
```python
Navvy(
    agent: Agent, # LLM https://ai.pydantic.dev/agents/
    project_path: str, # Repository path, if no repository is found a new one will be created
    project_url: str = None, # If provided, it will be used to clone a repository from the URL to the specified project_path
    author: str = "Navvy", # Commit author name
    author_address: str = "github.com/itsrofly/navvy-package" # Commit author address
)
```

## Requirements

Git            
Python 3.8 or higher.