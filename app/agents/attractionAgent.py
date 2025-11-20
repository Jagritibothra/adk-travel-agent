"""
AttractionAgent — ADK LlmAgent + HTTP A2A wrapper.

uses google_search tool (ADK-provided) to fetch attractions.
Hybrid extraction: attempts to extract ticket price & timeRequired from snippets; falls back to defaults.
"""

import logging
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search  # built-in tool
from ..prompts.prompts import attractionPrompt

logger = logging.getLogger("attractionAgent")
print("✅ attractionAgent module loaded")


# We expose google_search only to the attractionAgent (so it can call it)
# attractionAgent is still an LLM; it MUST output: short sentence + JSON (status + attractions list)
attractionAgent = LlmAgent(
    name="attractionAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=attractionPrompt,
    tools=[google_search],
)

root_agent = attractionAgent





