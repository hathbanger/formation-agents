from pathlib import Path
import os
from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.pprint import pprint_run_response

def get_urls_file(session_id):
    urls_file = Path(__file__).parent.joinpath("tmp", f"urls__{session_id}.md")
    urls_file.parent.mkdir(parents=True, exist_ok=True)
    return urls_file

class NewAgencyTeamWorkflow:
    """Workflow for generating a NYT-worthy article using a multi-agent team."""
    def __init__(self, session_id: str = None, debug_mode: bool = False):
        self.session_id = session_id or "default"
        self.urls_file = get_urls_file(self.session_id)
        self.searcher = Agent(
            name="Searcher",
            role="Searches the top URLs for a topic",
            instructions=[
                "Given a topic, first generate a list of 3 search terms related to that topic.",
                "For each search term, search the web and analyze the results.Return the 10 most relevant URLs to the topic.",
                "You are writing for the New York Times, so the quality of the sources is important.",
            ],
            tools=[DuckDuckGoTools()],
            add_datetime_to_instructions=True,
        )
        self.writer = Agent(
            name="Writer",
            role="Writes a high-quality article",
            description=(
                "You are a senior writer for the New York Times. Given a topic and a list of URLs, "
                "your goal is to write a high-quality NYT-worthy article on the topic."
            ),
            instructions=[
                "First read all urls using `read_article`."
                "Then write a high-quality NYT-worthy article on the topic."
                "The article should be well-structured, informative, engaging and catchy.",
                "Ensure the length is at least as long as a NYT cover story -- at a minimum, 15 paragraphs.",
                "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
                "Focus on clarity, coherence, and overall quality.",
                "Never make up facts or plagiarize. Always provide proper attribution.",
                "Remember: you are writing for the New York Times, so the quality of the article is important.",
            ],
            tools=[Newspaper4kTools()],
            add_datetime_to_instructions=True,
        )
        self.editor = Team(
            name="Editor",
            mode="coordinate",
            model=OpenAIChat("gpt-4o"),
            members=[self.searcher, self.writer],
            description="You are a senior NYT editor. Given a topic, your goal is to write a NYT worthy article.",
            instructions=[
                "First ask the search journalist to search for the most relevant URLs for that topic.",
                "Then ask the writer to get an engaging draft of the article.",
                "Edit, proofread, and refine the article to ensure it meets the high standards of the New York Times.",
                "The article should be extremely articulate and well written. "
                "Focus on clarity, coherence, and overall quality.",
                "Remember: you are the final gatekeeper before the article is published, so make sure the article is perfect.",
            ],
            add_datetime_to_instructions=True,
            send_team_context_to_members=True,
            markdown=True,
            debug_mode=debug_mode,
            show_members_responses=True,
        )

    def run(self, query: str):
        responses = list(self.editor.run(query, stream=False))
        for resp in reversed(responses):
            if hasattr(resp, "content") and resp.content and resp.content.strip() and resp.content.strip() != ")":
                return resp.content
        return "No content generated."

if __name__ == "__main__":
    import random
    from rich.prompt import Prompt

    if os.getenv("RUN_AS_API", "0") == "1":
        from agent_api_server import create_agent_api
        import uvicorn

        def workflow_runner(query):
            session_id = f"new-agency-team-{query.lower().replace(' ', '-')}"
            workflow = NewAgencyTeamWorkflow(session_id=session_id, debug_mode=True)
            result = workflow.editor.run(query, stream=False)
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

        app = create_agent_api("new-agency-team", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        example_prompts = [
            "Write an article about latest developments in AI.",
            "Write a NYT-worthy article about climate change policy.",
            "Write a feature on the future of electric vehicles.",
            "Write an in-depth piece on the impact of social media on elections.",
        ]
        query = Prompt.ask(
            "[bold]Enter an article topic[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        session_id = f"new-agency-team-{query.lower().replace(' ', '-')}"
        workflow = NewAgencyTeamWorkflow(session_id=session_id, debug_mode=True)
        responses = workflow.editor.run(query, stream=True)
        pprint_run_response(responses, markdown=True)