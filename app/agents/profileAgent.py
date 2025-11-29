# src/agents/profileAgent.py
import os, logging, requests
from typing import Dict, Any
from google.adk.agents.llm_agent import Agent
from ..prompts.prompts import orchestratorInstruction  # reuse for now or define profile-specific prompt

logger = logging.getLogger("profileAgent")
logging.basicConfig(level=logging.INFO)

MCP_BASE = os.getenv("MCP_HOST_URL","http://localhost:8600")
SEARCH_PROFILE_URL = f"{MCP_BASE}/tool/searchUserProfile"
SEARCH_TRIPS_URL = f"{MCP_BASE}/tool/searchTrips"
TIMEOUT = float(os.getenv("MCP_REQUEST_TIMEOUT","8.0"))

def getUserProfile(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload: { "userId": "...", "email": "..." }
    Returns profile JSON and recent trips.
    """
    try:
        r = requests.post(SEARCH_PROFILE_URL, json=payload, timeout=TIMEOUT); r.raise_for_status()
        profile_data = r.json()
        trips = {"status":"success","results":[]}
        userId = payload.get("userId") or (profile_data.get("results") and profile_data["results"][0].get("userId"))
        if userId:
            tr = requests.post(SEARCH_TRIPS_URL, json={"userId": userId}, timeout=TIMEOUT); tr.raise_for_status()
            trips = tr.json()
        return {"status":"success","profile": profile_data.get("results",[]), "trips": trips.get("results", [])}
    except Exception as e:
        logger.exception("getUserProfile failed")
        return {"status":"error","message": str(e)}

profileAgent = Agent(
    model="gemini-2.5-flash",
    name="profileAgent",
    description="Profile & memory agent - fetch user preferences and past trips via MCP.",
    instruction="Profile Agent - fetch user profile and trips using MCP tools.",
    tools=[getUserProfile],
)

if __name__ == "__main__":
    from flask import Flask, request, jsonify
    app = Flask("profileAgentService")
    port = int(os.getenv("PROFILE_AGENT_PORT","8504"))

    @app.get("/health")
    def health():
        return jsonify({"status":"ok","agent":"profileAgent"})

    @app.post("/tool/getUserProfile")
    def http_get_user_profile():
        payload = request.get_json(force=True, silent=True) or {}
        resp = getUserProfile(payload)
        return jsonify(resp), (200 if resp.get("status")=="success" else 500)

    app.run(host="0.0.0.0", port=port)
