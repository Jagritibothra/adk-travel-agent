"""
ConversationalAgent — ADK LlmAgent.

Key behavior:
- Parse natural prompt
- Use AgentTool 'plannerAgent.plan_trip' (ADK will execute the tool, here backed by A2A HTTP) 
- Format concise natural-language summary (A1) from returned itinerary JSON
- If user asked for export, call exportAgent via its AgentTool (A2A)
- uses plannerAgent as an AgentTool.
"""

import logging
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..prompts.prompts import conversationalPrompt
from .plannerAgent import root_agent as plannerAgent

logger = logging.getLogger("conversationAgent")
print("✅ conversationAgent module loaded")

conversationAgent = LlmAgent(
    name="conversationAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=conversationalPrompt,
    tools=[AgentTool(plannerAgent)],
)

root_agent = conversationAgent




