# WanderBot: Autonomous AI Travel Planner

## 🌍 Core Purpose of the Application
WanderBot is designed to **eliminate the complexity of travel planning** by automating every step of the process. Unlike traditional chatbots that only provide suggestions, WanderBot executes real-world actions through **multi-agent orchestration and live API calls**. Users simply describe their travel intent in natural language, and the system:

- Extracts structured trip details (destination, dates, budget)
- Searches flights, hotels, and attractions dynamically using APIs
- Generates a **multi-day itinerary** with human-friendly recommendations
- Stores itineraries and user preferences for future personalization

This transforms the travel experience into a **hands-off concierge service**, reducing planning time from hours to seconds.

---

## ✅ Problem Statement
Current travel planning tools require **manual effort** across multiple platforms. Users must:
- Search flights and hotels separately
- Compare prices and ratings manually
- Build itineraries without personalization

This fragmented process is inefficient and prone to errors. AI assistants today only provide **verbal suggestions**, not actionable itineraries.

---

## ✅ Solution
WanderBot introduces a **deterministic multi-agent architecture** where:
- Each agent performs **one specific role** (e.g., flight search, hotel retrieval)
- Agents communicate via **Model Context Protocol (MCP)** for tool invocation
- Real-time APIs ensure **up-to-date travel data**
- User memory enables **personalized recommendations** over time

This approach guarantees **accuracy, reliability, and scalability**.

---

## 📌 Abstract
WanderBot demonstrates **agentic reasoning combined with tool-based execution**. The system uses:
- **Conversation Agent**: Converts free-form text into structured trip parameters
- **Planner Agent**: Orchestrates workflow and ensures deterministic execution
- **Worker Agents**: Fetch flights, hotels, and attractions using MCP tools and A2A
- **Persistence Layer**: Stores itineraries and user profiles for personalization

Unlike static recommendation engines, WanderBot adapts dynamically to user preferences and real-world data.

---

## 🧱 Architecture & Flow
```mermaid
graph TD;
    User --> ConversationAgent;
    ConversationAgent --> PlannerAgent;
    PlannerAgent --> FlightAgent;
    PlannerAgent --> HotelAgent;
    PlannerAgent --> AttractionAgent;
    PlannerAgent --> ExportAgent;
    FlightAgent --> MCP (mock data, as of now);
    HotelAgent --> MCP (mock data, as of now);
    AttractionAgent --> Google_search;
    ExportAgent --> Persistence;
```

### Why This Architecture?
- **Planner → Worker Model** ensures strict control over execution order
- **No freelancing agents**: prevents unpredictable behavior
- **MCP tools** provide real-world data access without exposing raw APIs to LLMs

---

## 🔹 Step-by-Step Flow
1. **User Input**: "Plan a 5-day trip to Paris from Dec 10 to Dec 15 under $2000 budget"
2. **Conversation Agent**: Extracts structured fields → `{destination: Paris, dates: Dec 10-15, budget: 2000}`
3. **Planner Agent**: Calls `flightAgent()` → retrieves best flight
4. **Planner Agent**: Calls `hotelAgent()` → retrieves hotel options
5. **Planner Agent**: Calls `attractionAgent()` → fetches attractions
6. **Planner Agent**: Calls `exportAgent()` → saves itinerary + user profile
7. **Conversation Agent**: Returns **human-friendly itinerary summary**

---

## 🔍 Agent-by-Agent Responsibilities
| Agent | Role | Internal Logic |
|-------|------|---------------|
| ConversationAgent | Intent extraction | Uses NLP to parse dates, destination, budget |
| PlannerAgent | Orchestrator | Maintains execution graph, retries failed steps |
| FlightAgent | Flight search | Calls MCP tool → RapidAPI flight API |
| HotelAgent | Hotel search | Filters by budget & rating |
| AttractionAgent | Discovery | Uses Google Search MCP tool for attractions |
| ExportAgent | Persistence | Stores itinerary in JSON/DB and updates user profile |

---

## ⚙ MCP Tooling & Invocation Pattern
| Tool | Purpose | Example Invocation |
|------|---------|---------------------|
| searchFlights | Fetch flights | `mcp.invoke('searchFlights', params)` |
| searchHotels | Fetch hotels | `mcp.invoke('searchHotels', params)` |
| google_search | Attractions | `mcp.invoke('google_search', query)` |
| persist_itinerary | Save itinerary | `mcp.invoke('persist_itinerary', itinerary)` |

**Why MCP?** It provides a **secure, structured interface** between LLM agents and external APIs, preventing prompt injection and uncontrolled API calls.

---

## 🧠 Prompt Design Philosophy
- **Role Isolation**: Each agent receives only relevant context
- **Tool-First Execution**: Prompts instruct agents to call tools, not hallucinate data
- **Example**:
```
You are FlightAgent. Input: {destination: Paris, dates: Dec 10-15}. Task: Call searchFlights tool and return best option.
```

---

## ⚙ Detailed Setup Instructions
```bash
# 1. Clone the repository
git clone https://github.com/Jagritibothra/adk-travel-agent
cd adk-travel-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env
```
**Why these steps?**
- Cloning ensures you have the latest code
- Dependencies include MCP SDK, LLM libraries, and API clients
- `.env` stores sensitive keys securely

---

## 🔑 API Key Setup Guide
Add your keys in `.env`:
```
RAPIDAPI_KEY=your_rapidapi_key
GOOGLE_API_KEY=your_google_api_key
```
**Why?** These keys authenticate your requests to external APIs for flights, hotels, and attractions.

---

## 🧾 Mock JSON Examples with Schema Explanation
### Flight Search Response
```json
[
  {
    "flightId": "F001",
    "airline": "SpiceJet",
    "source": "DEL",
    "sourceCity": "Delhi",
    "destination": "BLR",
    "destinationCity": "Bangalore",
    "departureDate": "2025-02-12",
    "arrivalDate": "2025-02-12",
    "departureTime": "05:50",
    "arrivalTime": "08:15",
    "durationMinutes": 145,
    "stops": 0,
    "class": "Economy",
    "price": 4890
  },
  {
    "flightId": "F002",
    "airline": "IndiGo",
    "source": "BOM",
    "sourceCity": "Mumbai",
    "destination": "BLR",
    "destinationCity": "Bangalore",
    "departureDate": "2025-03-04",
    "arrivalDate": "2025-03-04",
    "departureTime": "13:05",
    "arrivalTime": "14:45",
    "durationMinutes": 100,
    "stops": 0,
    "class": "Economy",
    "price": 4150
  },
  {
    "flightId": "F003",
    "airline": "Vistara",
    "source": "DEL",
    "sourceCity": "Delhi",
    "destination": "BLR",
    "destinationCity": "Bangalore",
    "departureDate": "2025-04-02",
    "arrivalDate": "2025-04-02",
    "departureTime": "18:20",
    "arrivalTime": "20:50",
    "durationMinutes": 150,
    "stops": 0,
    "class": "Economy",
    "price": 5290
  },..]
```
**Schema**:
- `airline`: String
- `price`: Number (USD)
- `departure` & `arrival`: ISO datetime

### Hotel Search Response
```json
[
  {
    "hotelId": "H001",
    "name": "Blue Horizon Inn",
    "city": "Bangalore",
    "rating": 4.2,
    "pricePerNight": 3500,
    "amenities": ["WiFi", "Breakfast", "Gym", "Parking"],
    "roomType": "Deluxe",
    "distanceFromCenterKm": 3.1
  },
  {
    "hotelId": "H002",
    "name": "GreenLeaf Suites",
    "city": "Bangalore",
    "rating": 4.5,
    "pricePerNight": 4800,
    "amenities": ["WiFi", "Breakfast", "Pool", "Gym"],
    "roomType": "Executive",
    "distanceFromCenterKm": 2.0
  },
  {
    "hotelId": "H003",
    "name": "BudgetStay MG Road",
    "city": "Bangalore",
    "rating": 3.8,
    "pricePerNight": 2100,
    "amenities": ["WiFi", "Breakfast", "AC"],
    "roomType": "Standard",
    "distanceFromCenterKm": 1.8
  },..]
```
**Schema**:
- `name`: String
- `price_per_night`: Number
- `rating`: Float (1-5)

---

## ▶ Example Input → Example Output
**Input:**
```
Plan a 5-day trip to Paris from Dec 10 to Dec 15 under $2000 budget.
```
**Output:**
```
Your Paris itinerary is ready! ✈️
- Flight: Delta Airlines, Dec 10, $450
- Hotel: Hilton Downtown, $120/night
- Attractions: Eiffel Tower, Louvre Museum, Seine River Cruise, Montmartre Walk
```

---

## 🚀 Future Enhancements (with Feasibility Notes)
- **Multi-city trips**: Requires graph-based itinerary planning
- **Ride-sharing integration**: Add Uber/Lyft APIs via MCP tools
- **Dynamic budget optimization**: Implement constraint-based optimization algorithms
- **Voice interaction**: Integrate speech-to-text and text-to-speech modules

---

## 👤 Author & Acknowledgements
**Author:** Jagriti Bothra
**Acknowledgements:** Thanks to MCP open-source community and RapidAPI providers.