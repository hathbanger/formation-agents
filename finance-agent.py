from textwrap import dedent
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response

class FinanceAgentWorkflow:
    """Workflow for financial market analysis and reporting."""
    def __init__(self, session_id: str = None, storage=None, debug_mode: bool = False):
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                YFinanceTools(
                    stock_price=True,
                    analyst_recommendations=True,
                    stock_fundamentals=True,
                    historical_prices=True,
                    company_info=True,
                    company_news=True,
                )
            ],
            instructions=dedent("""
                You are a seasoned Wall Street analyst with deep expertise in market analysis! 📊

                Follow these steps for comprehensive financial analysis:
                1. Market Overview
                   - Latest stock price
                   - 52-week high and low
                2. Financial Deep Dive
                   - Key metrics (P/E, Market Cap, EPS)
                3. Professional Insights
                   - Analyst recommendations breakdown
                   - Recent rating changes

                4. Market Context
                   - Industry trends and positioning
                   - Competitive analysis
                   - Market sentiment indicators

                Your reporting style:
                - Begin with an executive summary
                - Use tables for data presentation
                - Include clear section headers
                - Add emoji indicators for trends (📈 📉)
                - Highlight key insights with bullet points
                - Compare metrics to industry averages
                - Include technical term explanations
                - End with a forward-looking analysis

                Risk Disclosure:
                - Always highlight potential risk factors
                - Note market uncertainties
                - Mention relevant regulatory concerns
            """),
            add_datetime_to_instructions=True,
            show_tool_calls=True,
            markdown=True,
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
            workflow = FinanceAgentWorkflow(
                session_id=f"finance-agent-{query.lower().replace(' ', '-')}",
                storage=SqliteStorage(
                    table_name="finance_agent_workflows",
                    db_file="tmp/agno_workflows.db",
                ),
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

        app = create_agent_api("finance-agent", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        # CLI example prompts
        example_prompts = [
            "What's the latest news and financial performance of Apple (AAPL)?",
            dedent("""
            Analyze the semiconductor market performance focusing on:
            - NVIDIA (NVDA)
            - AMD (AMD)
            - Intel (INTC)
            - Taiwan Semiconductor (TSM)
            Compare their market positions, growth metrics, and future outlook."""),
            dedent("""
            Evaluate the automotive industry's current state:
            - Tesla (TSLA)
            - Ford (F)
            - General Motors (GM)
            - Toyota (TM)
            Include EV transition progress and traditional auto metrics."""),
        ]
        query = Prompt.ask(
            "[bold]Enter a financial analysis query[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        url_safe_query = query.lower().replace(" ", "-")
        workflow = FinanceAgentWorkflow(
            session_id=f"finance-agent-{url_safe_query}",
            storage=SqliteStorage(
                table_name="finance_agent_workflows",
                db_file="tmp/agno_workflows.db",
            ),
            debug_mode=True,
        )
        responses = workflow.agent.run(query, stream=True)
        pprint_run_response(responses, markdown=True)

# More example prompts to explore:
"""
Advanced analysis queries:
1. "Compare Tesla's valuation metrics with traditional automakers"
2. "Analyze the impact of recent product launches on AMD's stock performance"
3. "How do Meta's financial metrics compare to its social media peers?"
4. "Evaluate Netflix's subscriber growth impact on financial metrics"
5. "Break down Amazon's revenue streams and segment performance"

Industry-specific analyses:
Semiconductor Market:
1. "How is the chip shortage affecting TSMC's market position?"
2. "Compare NVIDIA's AI chip revenue growth with competitors"
3. "Analyze Intel's foundry strategy impact on stock performance"
4. "Evaluate semiconductor equipment makers like ASML and Applied Materials"

Automotive Industry:
1. "Compare EV manufacturers' production metrics and margins"
2. "Analyze traditional automakers' EV transition progress"
3. "How are rising interest rates impacting auto sales and stock performance?"
4. "Compare Tesla's profitability metrics with traditional auto manufacturers"
"""