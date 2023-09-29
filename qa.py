import dotenv
import os
import fire
from typing import Optional
from llama_index import VectorStoreIndex
from llama_index.tools.query_engine import QueryEngineTool
from llama_index.objects import ObjectIndex, SimpleToolNodeMapping
from llama_index.query_engine import ToolRetrieverRouterQueryEngine
from llama_hub.github_repo import GithubRepositoryReader, GithubClient
from llama_hub.github_repo_issues import GitHubRepositoryIssuesReader, GitHubIssuesClient


dotenv.load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")


EMBEDDING_MODEL = "text-embedding-ada-002"


def get_user_input(prefix="Ask a question about the ControlNet Model: "):
    return input(prefix)


def main(
    model: str = 'gpt-3.5-turbo',
    owner: str = 'openai',
    repo_name: str = 'openai-python',
    branch: Optional[str] = 'main',
    commit_sha: Optional[str] = None,
    verbose: bool = False,
    include_file_extensions: list[str] = ['.py', '.md', '.yml', '.yaml', '.txt', '.ipynb'],
    concurrent_requests: int = 10,
):
    if branch is not None and commit_sha is not None:
        raise ValueError("Cannot specify both branch and commit_sha")

    # setup llama repo loader, load docs, create index, and query engine
    github_client = GithubClient(github_token)
    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo_name,
        filter_directories=(["gpt_index", "docs"], GithubRepositoryReader.FilterType.INCLUDE),
        filter_file_extensions=(include_file_extensions, GithubRepositoryReader.FilterType.INCLUDE),
        verbose=verbose,
        concurrent_requests=concurrent_requests,
    )
    if branch is not None:
        for attempt in range(2):  # fallback to master branch if needed
            try:
                repo_docs = loader.load_data(branch=branch)
            except Exception as e:
                if branch == 'main':
                    print(f"Failed to load data from branch {branch}. Trying master")
                    branch = 'master'
                    continue
                else:
                    print(f"Failed to load data from {owner}/{repo_name} branch {branch}.")
                    raise e
    else:
        try:
            repo_docs = loader.load_data(commit_sha=commit_sha)
        except Exception as e:
            print(f"Failed to load data from {owner}/{repo_name} commit {commit_sha}.")
            raise e
    repo_index = VectorStoreIndex.from_documents(repo_docs)
    repo_query_engine = repo_index.as_query_engine(use_async=True)
    repo_tool = QueryEngineTool.from_defaults(
        query_engine=repo_query_engine,
        description="Useful for questions related to the codebase or documentation.")

    # setup llama issues loader, load docs, create index, and create query engine
    github_client = GitHubIssuesClient(github_token)
    loader = GitHubRepositoryIssuesReader(
        github_client,
        owner=owner,
        repo=repo_name,
        verbose=verbose,
    )
    issue_docs = loader.load_data()
    issue_index = VectorStoreIndex.from_documents(issue_docs)
    issue_query_engine = issue_index.as_query_engine(use_async=True)
    issue_tool = QueryEngineTool.from_defaults(
        query_engine=issue_query_engine,
        description="Useful for questions related to issues or code problems."
    )

    # Setup tools and router retrieval
    tool_mapping = SimpleToolNodeMapping.from_objects([repo_tool, issue_tool])
    object_index = ObjectIndex.from_objects([repo_tool, issue_tool], tool_mapping, VectorStoreIndex)
    query_engine = ToolRetrieverRouterQueryEngine(object_index.as_retriever())

    base_input_query = f"Ask a question about {owner}/{repo_name} on "
    if branch is None:
        user_query = base_input_query + f"commit {commit_sha}: "
    else:
        user_query = base_input_query + f"branch {branch}: "

    # QA loop
    Q = get_user_input(user_query)
    while True:
        if Q == '':
            break
        A = query_engine.query(Q)
        print(A)
        user_query = "Ask another question: "
        Q = get_user_input(user_query)


if __name__ == "__main__":
    fire.Fire(main)
