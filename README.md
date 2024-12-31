# Navvy

The navvy package is a Python-based automation tool for managing Git repositories. It leverages the OpenAI API to perform tasks such as editing, creating, and deleting files within a repository.

## Installation

You can install the Navvy package using pip:

```sh
pip install navvy
```

## Usage

```python
from navvy import Navvy

# Initialize Navvy
navvy = Navvy(project_path="./repo_project_path", api_key="your_openai_api_key")

# Send a message to create a snake game
chunks = navvy.send_message("Create a snake game!")

for chunk in chunks:
    print(chunk, end="", flush=True)
```

Here is an example of how to undo a commit using the Navvy package:

```python
from navvy import Navvy

# Initialize Navvy
# Using OPENAI_API_KEY environment variable
navvy = Navvy(project_path="./repo_project_path") 

# Send a message to create a snake game
chunks = navvy.send_message("Create a snake game!")

for chunk in chunks:
    print(chunk, end="", flush=True)

# Undo the last commit
navvy.undo_commit_changes()
```

## Requirements

Git            
Python 3.8 or higher.

Note: The project path need be initialized with Git.