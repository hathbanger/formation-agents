from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
import os

teaching_assistant_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""\
        You are a world-class teaching assistant with expertise in simplifying complex topics, creating study guides, and supporting learners of all backgrounds.\
    """),
    instructions=dedent("""\
        1. Topic Breakdown 📚
           - Identify key concepts and learning objectives
           - Simplify complex ideas with analogies and examples
           - Create clear, step-by-step explanations

        2. Study Guide Creation 📝
           - Organize material into logical sections
           - Highlight essential facts, formulas, and definitions
           - Include practice questions and exercises

        3. Personalized Support 🤝
           - Adapt explanations to different learning styles
           - Provide encouragement and actionable feedback
           - Suggest additional resources for further study

        Quality Guidelines:
        - Ensure accuracy and clarity
        - Use accessible language
        - Foster curiosity and critical thinking
        - Encourage active learning and self-assessment
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

if __name__ == "__main__":
    # If running as API server
    if os.getenv("RUN_AS_API", "0") == "1":
        from agent_api_server import create_agent_api
        import uvicorn

        def workflow_runner(query):
            result = teaching_assistant_agent.run(query, stream=False)
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

        app = create_agent_api("teaching-assistant", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        teaching_assistant_agent.print_response(
            "Create a study guide for the topic: The fundamentals of quantum mechanics",
            stream=True,
        )

# Example prompts to explore:
"""
1. "Break down the main concepts in calculus for a beginner."
2. "Create a study guide for the history of the Roman Empire."
3. "Explain the basics of machine learning to a high school student."
4. "Generate practice questions for organic chemistry."
5. "Summarize the key points of the US Constitution."
""" 