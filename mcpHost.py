import json, logging, os
from pathlib import Path
from typing import Dict, Any
from flask import Flask, request, jsonify
from datetime import time
from math import radians, cos, sin, asin, sqrt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcpHost")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "mock-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load(p: Path):
    if not p.exists(): return []
    with p.open("r", encoding="utf-8") as f:
        d = json.load(f)
        return d if isinstance(d, list) else [d]

FLIGHTS = _load(DATA_DIR / "flights.json")
HOTELS = _load(DATA_DIR / "hotels.json")
ATTRACTIONS = _load(DATA_DIR / "attractions.json")
USERS = _load(DATA_DIR / "users.json")
TRIPS = _load(DATA_DIR / "trips.json")

def _parse_time(hhmm: str):
    try:
        hh, mm = hhmm.split(":")
        from datetime import time as dtime
        return dtime(int(hh), int(mm))
    except Exception:
        return None

def _is_in_window(hhmm: str, window_name: str):
    t = _parse_time(hhmm)
    if not t: return False
    windows = {
        "early_morning": (time(4,0), time(9,0)),
        "morning": (time(6,0), time(11,0)),
        "afternoon": (time(12,0), time(16,59)),
        "evening": (time(17,0), time(21,0)),
        "night": (time(22,0), time(23,59))
    }
    start, end = windows.get(window_name, (None,None))
    if not start: return True
    return start <= t <= end

def _load_json_file(name):
    p = DATA_DIR / name
    return _load(p)

def _match_city_or_code(value: str, candidate_codes: list, candidate_cities: list):
    # helper: normalize and match either IATA code or city name
    v = (value or "").strip().lower()
    if not v: return False
    # direct code match
    if v in (c.lower() for c in candidate_codes): return True
    # city name match
    if v in (c.lower() for c in candidate_cities): return True
    return False

def search_flights_tool(payload: Dict[str,Any]):
    try:
        for k in ("source","destination","date"):
            if not payload.get(k): return {"status":"error","message":f"Missing {k}"}
        src = payload["source"].strip()
        dst = payload["destination"].strip()
        date = payload["date"]
        non_stop = payload.get("nonStop", True)
        timeWindow = payload.get("timeWindow")
        limit = int(payload.get("limit", 5))
        results = []
        for f in FLIGHTS:
            codes = [f.get("source",""), f.get("destination","")]
            cities = [f.get("sourceCity",""), f.get("destinationCity","")]
            if f.get("departureDate") != date: continue
            # match both ends: allow either code or city name as input
            if not (_match_city_or_code(src, [f.get("source","")], [f.get("sourceCity","")]) and
                    _match_city_or_code(dst, [f.get("destination","")], [f.get("destinationCity","")])):
                continue
            results.append(f)
        if non_stop:
            results = [f for f in results if int(f.get("stops", 1))==0]
        if timeWindow:
            results = [f for f in results if _is_in_window(f.get("departureTime",""), timeWindow)]
        def key_fn(f):
            price = float(f.get("price",1e9))
            duration = int(f.get("durationMinutes", 1e9))
            dep = f.get("departureTime","99:99")
            return (price, duration, dep)
        results.sort(key=key_fn)
        return {"status":"success","count":len(results),"results":results[:limit]}
    except Exception as e:
        logger.exception("search_flights_tool")
        return {"status":"error","message":str(e)}

def search_hotels_tool(payload: Dict[str,Any]):
    try:
        if not payload.get("city"): return {"status":"error","message":"Missing city"}
        city = payload["city"].strip().lower()
        maxPrice = payload.get("maxPrice")
        minRating = payload.get("minRating")
        limit = int(payload.get("limit", 5))
        hs = [h for h in HOTELS if h.get("city","").strip().lower()==city]
        if maxPrice is not None:
            try: mp = float(maxPrice); hs = [h for h in hs if float(h.get("pricePerNight", 1e9)) <= mp]
            except: pass
        if minRating is not None:
            try: mr = float(minRating);
            except: mr = None
            if mr is not None:
                hs = [h for h in hs if float(h.get("rating", h.get("review_score",0))) >= mr]
        def hotel_key(h):
            score = float(h.get("review_score", h.get("rating", 0)))
            price = float(h.get("pricePerNight", 1e9))
            return (-score, price)
        hs.sort(key=hotel_key)
        return {"status":"success","count":len(hs),"results":hs[:limit]}
    except Exception as e:
        logger.exception("search_hotels_tool")
        return {"status":"error","message":str(e)}

def persist_itinerary_tool(payload: Dict[str,Any]):
    try:
        if not payload.get("userId") or not payload.get("itinerary"):
            return {"status":"error","message":"Missing userId or itinerary"}
        new_trip = {"userId": payload["userId"], "itinerary": payload["itinerary"], "meta": payload.get("meta", {})}
        TRIPS.append(new_trip)
        with open(DATA_DIR / "trips.json", "w", encoding="utf-8") as fh:
            json.dump(TRIPS, fh, indent=2, ensure_ascii=False)
            
        return {"status":"success","message":"itinerary persisted","trip": new_trip}
    except Exception as e:
        logger.exception("persist_itinerary_tool")
        return {"status":"error","message":str(e)}

from flask import Flask, request, jsonify
app = Flask("mcpHost")

@app.get("/health")
def health():
    print("Health check performed")
    return jsonify({"status":"ok","service":"mcpHost"})

@app.post("/tool/searchFlights")
def http_search_flights():
    print("Calling search_flights_tool...")
    return jsonify(search_flights_tool(request.get_json(force=True, silent=True) or {}))

@app.post("/tool/searchHotels")
def http_search_hotels():
    print("Calling search_hotels_tool...")
    return jsonify(search_hotels_tool(request.get_json(force=True, silent=True) or {}))

@app.post("/tool/persistItinerary")
def http_persist_itinerary():
    print("Calling persist_itinerary_tool...")
    return jsonify(persist_itinerary_tool(request.get_json(force=True, silent=True) or {}))

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8600"))
    logger.info(f"Starting MCP host on port {port}")
    app.run(host="0.0.0.0", port=port)
