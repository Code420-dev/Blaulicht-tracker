import requests
import time
import random
import re
import streamlit as st


STATE_CODES = {
    "Baden-Württemberg": "BW", "Bayern": "BY", "Berlin": "BE", 
    "Brandenburg": "BB", "Bremen": "HB", "Hamburg": "HH", 
    "Hessen": "HE", "Mecklenburg-Vorpommern": "MV", "Niedersachsen": "NI", 
    "Nordrhein-Westfalen": "NW", "Rheinland-Pfalz": "RP", "Saarland": "SL", 
    "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Schleswig-Holstein": "SH", 
    "Thüringen": "TH"
}

@st.cache_data(ttl=86400, show_spinner=False)
def get_location_info(location_input):
    """
    Fetches coordinates using Open-Meteo with a smart fallback 
    so it never fails on valid German cities.
    """
    clean_input = location_input.split(',')[0].strip()
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={clean_input}&count=5&language=de&format=json"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                
                for res in data["results"]:
                    cc = str(res.get("country_code", "")).upper()
                    if cc == "DE" or "Germany" in str(res.get("country", "")):
                        state = res.get('admin1', 'Hessen')
                        return {
                            "lat": float(res['latitude']),
                            "lon": float(res['longitude']),
                            "city": res.get('name', clean_input),
                            "state": state,
                            "state_code": STATE_CODES.get(state, "HE")
                        }
                
                
                res = data["results"][0]
                state = res.get('admin1', 'Hessen')
                return {
                    "lat": float(res['latitude']),
                    "lon": float(res['longitude']),
                    "city": res.get('name', clean_input),
                    "state": state,
                    "state_code": STATE_CODES.get(state, "HE")
                }
    except Exception as e:
        pass
        
    return None

def get_incident_coordinates(city, district, fallback_lat, fallback_lon):
    """Attempts to find exact coordinates for an incident district."""
    generic_labels = ["City Area", "Major Roads", "Local Area", "Region-wide", "Specific Street / Route"]
    
    if district not in generic_labels:
        if re.match(r'^A\s?\d+', district):
            query = f"{district}, Germany"
        else:
            query = f"{district}, {city}, Germany"
            
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {'User-Agent': 'Fares-Portfolio-App/2.0'}
        
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data:
                    time.sleep(0.5) 
                    return float(data[0]['lat']), float(data[0]['lon'])
        except Exception as e:
            pass 
            
    # Scatter fallback
    offset_lat = fallback_lat + random.uniform(-0.025, 0.025)
    offset_lon = fallback_lon + random.uniform(-0.025, 0.025)
    
    return offset_lat, offset_lon