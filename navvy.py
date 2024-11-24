import os
import json
from git import Repo
from pathlib import Path
from openai import OpenAI


class Navvy:
    __tools = [
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": """
                    Use this function to edit/create the contents of files.
                    """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": """The path to the file you want to edit.""",
                        },
                        "file_content": {
                            "type": "string",
                            "description": """The new content of the file.""",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": """The message for the commit.""",
                        }
                    },
                    "required": ["file_path", "file_content", "commit_message"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": """
                    Use this function to delete files.
                    """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": """The path to the file you want to delete.""",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": """The message for the commit.""",
                        }
                    },
                    "required": ["file_path", "commit_message"],
                },
            }
        }
    ]

    def __init__(self, project_path, model="gpt-4o", system_messages=None) -> None:
        # Set the project path
        self.project_path = Path(project_path).resolve()
        self.repo = Repo(self.project_path)
        self.model = model
        self.system_messages = system_messages
        
        if (not self.repo.head.is_valid()):
            initial_commit_file = self.project_path / ".gitkeep"
            initial_commit_file.touch()
            self.repo.index.add([initial_commit_file])
            self.repo.index.commit("Starting Repository")


        if (not self.system_messages):
            self.system_messages = [
                {
                    "role": "system",
                    "content": """
                        You are a Software Developer, your job is to develop software.
                        """
                }
            ]

        # Initialize IA Chatbot
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.clear_chat_history()

    '''Public methods'''

    def send_message(self, message):
        chat = self.get_chat_history()

        # Add files from repo to the chat
        # Don't save directly to the chat history because the files can change and it's more economical.
        file_contents = self.__get_all_file_contents(
            self.repo.head.commit.tree)
        if not file_contents:
            file_contents = "No files in the repository."

        chat.append({
            "role": "system",
            "content": "files:" + file_contents
        })

        # Add last 3 commits messages to the chat
        chat.append({
            "role": "system",
            "content": "Last three commits:" + str(list(self.repo.iter_commits(max_count=3)))
        })

        chat.append({
            "role": "user",
            "content": message
        })

        self.chat_history.append({
            "role": "user",
            "content": message
        })
        functions = []

        response = self.client.chat.completions.create(
            messages=chat,
            model=self.model,
            tools=self.__tools,
            stream=True
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
            elif delta.tool_calls:
                tool_call = delta.tool_calls[0]
                function = tool_call.function

                if (tool_call.index == len(functions)):
                    functions.append({
                        "name": None,
                        "arguments": ""
                    })

                if function.name:
                    functions[tool_call.index]["name"] = function.name
                if function.arguments:
                    functions[tool_call.index]["arguments"] += function.arguments

        for function in functions:
            function_name = function["name"]
            function_arguments = json.loads(function["arguments"])

            if (function_name == "edit_file"):
                self.__edit_file(**function_arguments)
                yield f"\nModified file: {os.path.basename(function_arguments['file_path'])}"
            elif (function_name == "delete_file"):
                self.__delete_file(**function_arguments)
                yield f"\nRemoved file: {os.path.basename(function_arguments['file_path'])}"

    def get_chat_history(self):
        return self.chat_history.copy()

    def clear_chat_history(self) -> None:
        # Add system messages to the chat history
        self.chat_history = self.system_messages.copy()

    def undo_commit_changes(self, commit_id=None):
        if (not commit_id):
            last_commits = list(self.repo.iter_commits(max_count=2))
            last_element = last_commits[-1]
            commit_id = last_element.hexsha
        # Undo Commit
        self.repo.git.execute(["git", "reset", commit_id])

        # Discard all changes files in the project path
        self.repo.git.execute(
            ["git", "checkout", str(self.project_path / ".")])
        self.repo.git.execute(["git", "clean", "-fdx"])

    def get_all_commits_ids(self):
        # Get all commit ids (hexsha) & commit messages
        return [(commit.hexsha, commit.message) for commit in self.repo.iter_commits()]

    '''Private methods'''

    def __get_all_file_contents(self, root):
        contents = []
        for entry in root.traverse():
            if entry.type == 'blob':  # Check if the entry is a file
                file_path = entry.path
                try:
                    # Read and add file content to contents list
                    with open(self.project_path / file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        contents.append(f'File:{file_path}\n{file_content}\n')
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        return "\n".join(contents)

    def __edit_file(self, file_path, file_content, commit_message):
        # Ensure the directory exists
        complete_path = self.project_path / file_path
        os.makedirs(complete_path.parent, exist_ok=True)

        # Write the new content to the file
        with open(complete_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        # Add the file to the index
        self.repo.index.add([file_path])

        # Commit the changes
        self.repo.index.commit(commit_message)

    def __delete_file(self, file_path, commit_message):
        # Delete the file
        complete_path = (self.project_path / file_path)

        # Check if the file exists before attempting to delete
        if complete_path.exists():
            # Delete the file
            os.remove(complete_path)
        else:
            print(f"File not found: {self.project_path / file_path}")

        self.repo.git.add(update=True)
        # Commit the changes
        self.repo.index.commit(commit_message)
