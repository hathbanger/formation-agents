import asyncio
from textwrap import dedent
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.storage.sqlite import SqliteStorage
from agno.workflow import RunEvent, RunResponse, Workflow

reddit_researcher = Agent(
    name="Reddit Researcher",
    role="Research a topic on Reddit",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    You are a Reddit researcher.
    You will be given a topic to research on Reddit.
    You will need to find the most relevant posts on Reddit.
    """),
)

hackernews_researcher = Agent(
    name="HackerNews Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Research a topic on HackerNews.",
    tools=[HackerNewsTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    You are a HackerNews researcher.
    You will be given a topic to research on HackerNews.
    You will need to find the most relevant posts on HackerNews.
    """),
)

academic_paper_researcher = Agent(
    name="Academic Paper Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Research academic papers and scholarly content",
    tools=[GoogleSearchTools(), ArxivTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    You are a academic paper researcher.
    You will be given a topic to research in academic literature.
    You will need to find relevant scholarly articles, papers, and academic discussions.
    Focus on peer-reviewed content and citations from reputable sources.
    Provide brief summaries of key findings and methodologies.
    """),
)

twitter_researcher = Agent(
    name="Twitter Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Research trending discussions and real-time updates",
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    You are a Twitter/X researcher.
    You will be given a topic to research on Twitter/X.
    You will need to find trending discussions, influential voices, and real-time updates.
    Focus on verified accounts and credible sources when possible.
    Track relevant hashtags and ongoing conversations.
    """),
)

class DiscussionTeamWorkflow(Workflow):
    """Workflow for orchestrating a multi-agent discussion team on a given topic."""
    def __init__(self, session_id: str = None, storage=None, debug_mode: bool = False):
        self.team = Team(
            name="Discussion Team",
            mode="collaborate",
            model=OpenAIChat("gpt-4o"),
            members=[
                reddit_researcher,
                hackernews_researcher,
                academic_paper_researcher,
                twitter_researcher,
            ],
            instructions=[
                "You are a discussion master.",
                "You have to stop the discussion when you think the team has reached a consensus.",
            ],
            success_criteria="The team has reached a consensus.",
            send_team_context_to_members=True,
            update_team_context=True,
            show_tool_calls=True,
            markdown=True,
            debug_mode=debug_mode,
            show_members_responses=True,
            session_id=session_id,
            storage=storage,
        )

    def run(self, query: str):
        # Returns a string (markdown) response for the given query
        responses = list(asyncio.run(self.team.run(query, stream=False)))
        for resp in reversed(responses):
            if hasattr(resp, "content") and resp.content and resp.content.strip():
                return resp.content
        return "No content generated."

if __name__ == "__main__":
    import random
    from rich.prompt import Prompt

    if os.getenv("RUN_AS_API", "0") == "1":
        from agent_api_server import create_agent_api
        import uvicorn

        def workflow_runner(query):
            workflow = DiscussionTeamWorkflow(
                session_id=f"discussion-team-{query.lower().replace(' ', '-')}",
                storage=SqliteStorage(
                    table_name="discussion_team_workflows",
                    db_file="tmp/agno_workflows.db",
                ),
                debug_mode=True,
            )
            result = workflow.run(query)
            return result

        app = create_agent_api("discussion-team", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        example_prompts = [
            "What is the best way to learn to code?",
            "How will AI impact the future of work?",
            "What are the pros and cons of remote work?",
            "Is cryptocurrency a good investment?",
        ]
        query = Prompt.ask(
            "[bold]Enter a discussion topic[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        url_safe_query = query.lower().replace(" ", "-")
        workflow = DiscussionTeamWorkflow(
            session_id=f"discussion-team-{url_safe_query}",
            storage=SqliteStorage(
                table_name="discussion_team_workflows",
                db_file="tmp/agno_workflows.db",
            ),
            debug_mode=True,
        )
        responses = workflow.team.run(query, stream=True)
        from agno.utils.pprint import pprint_run_response
        pprint_run_response(responses, markdown=True)