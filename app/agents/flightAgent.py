"""
flightAgent — wrapper that calls MCP /tool/searchFlights (mock-data).
Exposes a function tool `search_flights_tool(payload)` for its internal LLM to use.
"""

import logging
from typing import Optional, Dict, Any
import requests

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from ..prompts.prompts import flightPrompt

logger = logging.getLogger("flightAgent")
logger.setLevel(logging.INFO)

# MCP endpoint (adjust host/port if needed)
MCP_SEARCH_FLIGHTS = "http://localhost:8600/tool/searchFlights"

def search_flights(
    source: str,
    destination: str,
    date: str,
    non_stop: bool = True,
    time_window: Optional[str] = None,
    preferred_airline: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Simple flat signature (primitives only) so ADK's function declaration parser can handle it.
    Calls MCP /tool/searchFlights and returns MCP JSON directly (wrap error if request fails).
    """
    print("Calling search_flights...")
    try:
        payload = {
            "source": (source or "").strip(),
            "destination": (destination or "").strip(),
            "date": date,
            "nonStop": bool(non_stop),
            "timeWindow": time_window,
            "preferredAirline": preferred_airline,
            "limit": int(limit),
        }
        # remove None values
        payload = {k: v for k, v in payload.items() if v is not None and v != ""}
        r = requests.post(MCP_SEARCH_FLIGHTS, json=payload, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.exception("search_flights failed")
        return {"status": "error", "message": str(e)}

# LLM Agent — expose the function as a tool by putting the function in `tools` list.
flight_agent = LlmAgent(
    name="flightAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=flightPrompt,
    tools=[search_flights],
)

root_agent = flight_agent




