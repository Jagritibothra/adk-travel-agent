"""
hotelAgent — wrapper that calls MCP /tool/searchHotels (mock-data).
Exposes a function tool `search_hotels_tool(payload)` for its internal LLM to use.
"""

import logging
from typing import Optional, Dict, Any
import requests

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from ..prompts.prompts import hotelPrompt

logger = logging.getLogger("hotelAgent")
logger.setLevel(logging.INFO)

MCP_SEARCH_HOTELS = "http://localhost:8600/tool/searchHotels"

def search_hotels(
    city: str,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    limit: int = 5
) -> Dict[str, Any]:
    print("Calling search_hotels...")
    """
    Flat parameters only. Returns MCP response.
    """
    try:
        payload = {"city": (city or "").strip(), "limit": int(limit)}
        if max_price is not None:
            payload["maxPrice"] = float(max_price)
        if min_rating is not None:
            payload["minRating"] = float(min_rating)
        r = requests.post(MCP_SEARCH_HOTELS, json=payload, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.exception("search_hotels failed")
        return {"status": "error", "message": str(e)}

hotel_agent = LlmAgent(
    name="hotelAgent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=hotelPrompt,
    tools=[search_hotels],
)

root_agent = hotel_agent


