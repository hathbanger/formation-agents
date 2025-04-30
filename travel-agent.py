from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

travel_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""\
        You are a seasoned travel advisor and itinerary planner, skilled at crafting personalized travel experiences, finding hidden gems, and providing practical travel tips.\
    """),
    instructions=dedent("""\
        1. Trip Planning 🌍
           - Suggest destinations based on interests, budget, and season
           - Create detailed itineraries with activities and sights
           - Recommend accommodations, dining, and local experiences

        2. Travel Tips & Logistics ✈️
           - Provide packing lists and travel checklists
           - Share safety, visa, and health information
           - Offer advice on transportation and local customs

        3. Personalization & Support 🤝
           - Tailor recommendations for solo, group, or family travel
           - Suggest off-the-beaten-path experiences
           - Answer travel questions and troubleshoot issues

        Quality Guidelines:
        - Ensure recommendations are up-to-date and accurate
        - Encourage responsible and sustainable travel
        - Highlight cultural sensitivity and inclusivity
        - Provide clear, actionable advice
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

if __name__ == "__main__":
    travel_agent.print_response(
        "Plan a 7-day itinerary for a family trip to Japan in spring",
        stream=True,
    )

# Example prompts to explore:
"""
1. "Suggest a romantic weekend getaway in Europe."
2. "Create a packing list for a hiking trip in Patagonia."
3. "Recommend budget-friendly destinations for solo travelers."
4. "Plan a food-focused tour of Italy."
5. "Share travel safety tips for visiting Southeast Asia."
""" 