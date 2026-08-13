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

# CACHE for 24 hours  to reduce spam on API
@st.cache_data(ttl=86400, show_spinner=False)
def get_location_info(location_input):
    """Fetches coordinates for a given city or zip code."""
    query = f"{location_input}, Germany"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=1"
    
    
    headers = {
        'User-Agent': 'Fares-Portfolio-App/1.0 (Frankfurt UAS Informatik)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                
                address = data[0].get('address', {})
                city = address.get('city', address.get('town', address.get('village', location_input)))
                state = address.get('state', 'Hessen')
                state_code = STATE_CODES.get(state, "HE")
                
                return {
                    "lat": lat,
                    "lon": lon,
                    "city": city.title(),
                    "state": state,
                    "state_code": state_code
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
        
        #  exact same unique ID for the pins too
        headers = {
            'User-Agent': 'Fares-Portfolio-App/1.0 (Frankfurt UAS Informatik)'
        }
        
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