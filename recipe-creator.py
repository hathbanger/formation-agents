from textwrap import dedent
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.pprint import pprint_run_response

class RecipeCreatorWorkflow:
    """Workflow for creative recipe generation and culinary guidance."""
    def __init__(self, session_id: str = None, storage=None, debug_mode: bool = False):
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[DuckDuckGoTools(), Newspaper4kTools()],
            description=dedent("""
                You are a creative recipe developer and culinary expert, skilled at inventing new dishes, adapting recipes for dietary needs, and providing step-by-step cooking guidance.\
            """),
            instructions=dedent("""
                1. Recipe Ideation 🍳
                   - Invent unique recipes or adapt classics
                   - Consider dietary restrictions and preferences
                   - Suggest ingredient substitutions

                2. Step-by-Step Instructions 📝
                   - Provide clear, detailed cooking steps
                   - Include preparation and cooking times
                   - Offer plating and serving suggestions

                3. Cooking Tips & Variations 🌱
                   - Share chef tips and tricks
                   - Suggest flavor pairings and enhancements
                   - Offer variations for different cuisines or occasions

                Quality Guidelines:
                - Ensure clarity and accuracy
                - Use accessible language
                - Encourage creativity and experimentation
                - Highlight food safety and allergen info
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
            workflow = RecipeCreatorWorkflow(
                session_id=f"recipe-creator-{query.lower().replace(' ', '-')}",
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

        app = create_agent_api("recipe-creator", workflow_runner)
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
    else:
        # CLI example usage
        example_prompts = [
            "Create a vegan lasagna recipe with step-by-step instructions",
            "Invent a gluten-free dessert for summer.",
            "Adapt a classic French dish for a keto diet.",
            "Create a meal plan for a week of Mediterranean dinners.",
            "Suggest ingredient swaps for nut allergies in baking.",
            "Write a recipe for a quick, healthy breakfast smoothie.",
        ]
        query = Prompt.ask(
            "[bold]Enter a recipe or cooking query[/bold] (or press Enter for a random example)\n✨",
            default=random.choice(example_prompts),
        )
        url_safe_query = query.lower().replace(" ", "-")
        workflow = RecipeCreatorWorkflow(
            session_id=f"recipe-creator-{url_safe_query}",
            debug_mode=True,
        )
        responses = workflow.agent.run(query, stream=True)
        pprint_run_response(responses, markdown=True)

# Example prompts to explore:
"""
1. "Invent a gluten-free dessert for summer."
2. "Adapt a classic French dish for a keto diet."
3. "Create a meal plan for a week of Mediterranean dinners."
4. "Suggest ingredient swaps for nut allergies in baking."
5. "Write a recipe for a quick, healthy breakfast smoothie."
""" 