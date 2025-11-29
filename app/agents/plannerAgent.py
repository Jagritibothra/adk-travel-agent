"""
plannerAgent

This agent plans trips by orchestrating subordinate agents:
 • flightAgent  (find flights)
 • hotelAgent   (find hotels)
 • attractionAgent (find attractions / build daily plan)
 • exportAgent  (save itinerary — only when invoked)

The planner does NOT implement business logic manually.
It takes formatted user-travel requirements and delegates work
to subtools via ADK AgentTools.

Output returned to caller (e.g. conversationAgent):
{
  "status": "success",
  "itinerary": {
        "flight": {...},
        "hotel": {...},
        "days": [
            { "date": "2025-12-02", "activities": [ {...}, {...} ] },
            ...
        ]
  }
}
"""

import logging
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types

from ..prompts.prompts import plannerPrompt
from .flightAgent import root_agent as flightAgent
from .hotelAgent import root_agent as hotelAgent
from .attractionAgent import root_agent as attractionAgent
from .exportAgent import root_agent as exportAgent

logger = logging.getLogger("plannerAgent")

retry_config = types.HttpRetryOptions(
    attempts=4, exp_base=5, initial_delay=1, http_status_codes=[429,500,503,504]
)

planner_agent = LlmAgent(
    name="plannerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=plannerPrompt,
    # Planner uses sub-agents as AgentTool (true agents)
    tools=[
        AgentTool(flightAgent),
        AgentTool(hotelAgent),
        AgentTool(attractionAgent),
        AgentTool(exportAgent),
    ],
)

print("plannerAgent initialized with sub-agents.")

root_agent = planner_agent


