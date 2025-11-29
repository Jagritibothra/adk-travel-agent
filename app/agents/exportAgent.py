"""
exportAgent — persist itinerary to MCP /tool/persistItinerary
"""

import logging
from typing import Dict, Any, Optional
import requests

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from ..prompts.prompts import exportPrompt

logger = logging.getLogger("exportAgent")
logger.setLevel(logging.INFO)

MCP_PERSIST = "http://localhost:8600/tool/persistItinerary"

def persist_itinerary(
    userId: str,
    itinerary: Dict[str, Any],
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Flat signature for ADK parsing. Calls MCP persist endpoint.
    """
    print("Calling persist_itinerary...")
    try:
        payload = {"userId": userId, "itinerary": itinerary, "meta": meta or {}}
        r = requests.post(MCP_PERSIST, json=payload, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.exception("persist_itinerary failed")
        return {"status": "error", "message": str(e)}

export_agent = LlmAgent(
    name="exportAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=exportPrompt,
    tools=[persist_itinerary],
)

root_agent = export_agent






