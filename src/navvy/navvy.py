import os
from git import Repo
from git import Actor
from pathlib import Path
from pydantic_ai import Agent


class Navvy:
    agent: Agent

    def __init__(self, agent: Agent, project_path: str, project_url: str = None, author: str = "Navvy", author_address: str = "github.com/itsrofly/navvy-package") -> None:
        # Set the project path
        self._project_path = Path(project_path).resolve()

        # Clone the project from the URL if provided
        if (project_url):
            self._repo = Repo.clone_from(project_url, self._project_path)
        else:
            try:  # Try loading the existing repository
                self._repo = Repo(self._project_path)
            except:
                # Initialize a new repository
                self._repo = Repo.init(self._project_path)
                # Create gitkeep file
                initial_commit_file = self._project_path / ".gitkeep"
                initial_commit_file.touch()
                # Add and commit the initial commit file
                self._repo.index.add([initial_commit_file])
                self._repo.index.commit(
                    "Starting Repository", author=Actor(author, author_address))

        # Set the agent
        self.agent = agent

        # Decorate the instance methods after self.agent is available
        self.__get_all_file_contents = self.agent.system_prompt(
            self.__get_all_file_contents)
        self.__get_all_commits_messages = self.agent.system_prompt(
            self.__get_all_commits_messages)
        self.__edit_file = self.agent.tool_plain(self.__edit_file)
        self.__delete_file = self.agent.tool_plain(self.__delete_file)

    '''Public methods'''

    def undo_commit_changes(self, commit_id: str = None) -> None:
        if (not commit_id):
            last_commits = list(self._repo.iter_commits(max_count=2))
            last_element = last_commits[-1]
            commit_id = last_element.hexsha
        # Undo Commit
        self._repo.git.execute(["git", "reset", commit_id])

        # Discard all changes files in the project path
        self._repo.git.execute(
            ["git", "checkout", str(self._project_path / ".")])
        self._repo.git.execute(["git", "clean", "-fdx"])

    def get_all_commits(self):
        # Get all commit ids (hexsha) & commit messages
        return [(commit.hexsha, commit.message) for commit in self._repo.iter_commits()]

    '''Private methods'''

    def __get_all_file_contents(self) -> str:
        root = self._repo.head.commit.tree

        contents = []
        for entry in root.traverse():
            if entry.type == 'blob':  # Check if the entry is a file
                file_path = entry.path
                try:
                    # Read and add file content to contents list
                    with open(self._project_path / file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        contents.append(f'File:{file_path}\n{file_content}\n')
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        if (not contents):
            return "No files found"
        return "\n".join(contents)

    def __get_all_commits_messages(self) -> str:
        return str([commit.message for commit in self._repo.iter_commits()])

    def __edit_file(self, file_path: str, file_content: str, commit_message: str) -> str:
        # Ensure the directory exists
        complete_path = self._project_path / file_path
        os.makedirs(complete_path.parent, exist_ok=True)

        # Write the new content to the file
        with open(complete_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        # Add the file to the index
        self._repo.index.add([file_path])

        # Commit the changes
        self._repo.index.commit(commit_message)
        return commit_message

    def __delete_file(self, file_path: str, commit_message: str) -> str:
        # Delete the file
        complete_path = (self._project_path / file_path)

        # Check if the file exists before attempting to delete
        if complete_path.exists():
            # Delete the file
            os.remove(complete_path)

        self._repo.git.add(update=True)
        # Commit the changes
        self._repo.index.commit(commit_message)
        return commit_message
