from textwrap import dedent
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.pprint import pprint_run_response

class MovieRecommenderWorkflow:
    """Workflow for movie recommendations and analysis."""
    def __init__(self, session_id: str = None, storage=None, debug_mode: bool = False):
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[DuckDuckGoTools(), Newspaper4kTools()],
            description=dedent("""
                You are a film buff and recommendation expert, skilled at suggesting movies for any mood, genre, or occasion, and providing thoughtful reviews and trivia.\
            """),
            instructions=dedent("""
                1. Movie Discovery 🎬
                   - Recommend films based on user preferences
                   - Suggest hidden gems and classics
                   - Tailor picks for mood, genre, or event

                2. Review & Analysis 📝
                   - Provide concise, spoiler-free reviews
                   - Highlight notable performances and direction
                   - Share interesting trivia and behind-the-scenes facts

                3. Watchlist & Theming 📋
                   - Curate themed watchlists (e.g., "Feel-Good Comedies", "Oscar Winners")
                   - Suggest double features or marathon lineups
                   - Recommend films for group or solo viewing

                Quality Guidelines:
                - Ensure recommendations are diverse and inclusive
                - Avoid spoilers unless requested
                - Encourage exploration of new genres and filmmakers
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
        responses = list(self.agent.run(query, stream=False))
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

        def workflow_runner(query):
            workflow = MovieRecommenderWorkflow(
                session_id=f"movie-recommender-{query.lower().replace(' ', '-')}",
                debug_mode=True,
            )
            result = workflow.agent.run(query, stream=False)
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

        app = create_agent_api("movie-recommender", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        # CLI example usage
        example_prompts = [
            "Recommend a list of uplifting movies for a rainy weekend",
            "Suggest sci-fi movies with strong female leads.",
            "Create a watchlist of classic noir films.",
            "Recommend family-friendly animated movies.",
            "List the best films directed by Christopher Nolan.",
            "Suggest movies for fans of psychological thrillers.",
        ]
        query = Prompt.ask(
            "[bold]Enter a movie recommendation query[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        url_safe_query = query.lower().replace(" ", "-")
        workflow = MovieRecommenderWorkflow(
            session_id=f"movie-recommender-{url_safe_query}",
            debug_mode=True,
        )
        responses = workflow.agent.run(query, stream=True)
        pprint_run_response(responses, markdown=True)

# Example prompts to explore:
"""
1. "Suggest sci-fi movies with strong female leads."
2. "Create a watchlist of classic noir films."
3. "Recommend family-friendly animated movies."
4. "List the best films directed by Christopher Nolan."
5. "Suggest movies for fans of psychological thrillers."
""" 