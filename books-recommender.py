from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response

import os

class BooksRecommenderWorkflow:
    """Workflow for book recommendations and literary analysis."""
    def __init__(self, session_id: str = None, storage=None, debug_mode: bool = False):
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[DuckDuckGoTools(), Newspaper4kTools()],
            description=dedent("""
                You are a literary expert and book recommendation specialist, skilled at suggesting books for any interest, age, or reading level, and providing thoughtful reviews and reading lists.
            """),
            instructions=dedent("""
                1. Book Discovery 📚
                   - Recommend books based on user interests and goals
                   - Suggest classics, new releases, and hidden gems
                   - Tailor picks for age, genre, or occasion

                2. Review & Analysis 📝
                   - Provide concise, spoiler-free reviews
                   - Highlight notable themes, writing styles, and authors
                   - Share interesting trivia and literary context

                3. Reading Lists & Theming 📋
                   - Curate themed reading lists (e.g., "Summer Beach Reads", "Award Winners")
                   - Suggest books for group or solo reading
                   - Recommend series or sequels for binge reading

                Quality Guidelines:
                - Ensure recommendations are diverse and inclusive
                - Avoid spoilers unless requested
                - Encourage exploration of new genres and authors
                - Provide content warnings where appropriate
            """),
            markdown=True,
            show_tool_calls=True,
            add_datetime_to_instructions=True,
            session_id=session_id,
            storage=storage,
            debug_mode=debug_mode,
        )

    def run(self, query: str):
        # Returns a string (markdown) response for the given query
        responses = list(self.agent.run(query, stream=False))
        # Find the last non-empty, non-trivial content
        for resp in reversed(responses):
            if resp.content and resp.content.strip() and resp.content.strip() != ")":
                return resp.content
        return "No content generated."

if __name__ == "__main__":
    import random
    from rich.prompt import Prompt

    # If running as API server
    if os.getenv("RUN_AS_API", "0") == "1":
        from agent_api_server import create_agent_api
        import uvicorn

        # API workflow runner: expects 'query' as input, returns markdown string
        def workflow_runner(query):
            recommender = BooksRecommenderWorkflow(
                session_id=f"books-recommender-{query.lower().replace(' ', '-')}",
                storage=SqliteStorage(
                    table_name="books_recommender_workflows",
                    db_file="tmp/agno_workflows.db",
                ),
                debug_mode=True,
            )
            # Robustly handle both single RunResponse and iterable returns
            result = recommender.agent.run(query, stream=False)
            if isinstance(result, (list, tuple)):
                responses = result
            elif hasattr(result, '__iter__') and not isinstance(result, str):
                responses = list(result)
            else:
                responses = [result]
            for resp in reversed(responses):
                if hasattr(resp, "content") and resp.content and resp.content.strip() and resp.content.strip() != ")":
                    return resp.content
            return "No content generated."

        app = create_agent_api("books-recommender", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        # CLI example usage
        example_prompts = [
            "Suggest science fiction books with strong world-building.",
            "Create a reading list of classic American literature.",
            "Recommend books for children learning to read.",
            "List the best novels by Haruki Murakami.",
            "Suggest books for fans of historical mysteries.",
            "Recommend a list of inspiring books for entrepreneurs",
        ]
        query = Prompt.ask(
            "[bold]Enter a book recommendation query[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        url_safe_query = query.lower().replace(" ", "-")
        recommender = BooksRecommenderWorkflow(
            session_id=f"books-recommender-{url_safe_query}",
            storage=SqliteStorage(
                table_name="books_recommender_workflows",
                db_file="tmp/agno_workflows.db",
            ),
            debug_mode=True,
        )
        responses = recommender.agent.run(query, stream=True)
        pprint_run_response(responses, markdown=True)

# Example prompts to explore:
"""
1. "Suggest science fiction books with strong world-building."
2. "Create a reading list of classic American literature."
3. "Recommend books for children learning to read."
4. "List the best novels by Haruki Murakami."
5. "Suggest books for fans of historical mysteries."
""" 