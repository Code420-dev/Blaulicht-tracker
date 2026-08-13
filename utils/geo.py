import math
import requests
import time
import random
import re 
def get_location_info(search_query):
    """
    Takes a city name (Berlin) or Zip Code (60316) and uses OpenStreetMap 
    to find the geographic data and State (Bundesland).
    """
    # Free OpenStreetMap Geocoding API
    url = f"https://nominatim.openstreetmap.org/search?q={search_query}&format=json&addressdetails=1&countrycodes=de&limit=1"
    
    # Nominatim requires a User-Agent header so they know who is using the free API
    headers = {'User-Agent': 'Student-Blaulicht-App/1.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return None
                
            place = data[0]
            address = place.get('address', {})
            
            # Map German State Names to NINA State Codes
            state_mapping = {
                "Hessen": "DE-HE", "Berlin": "DE-BE", "Bayern": "DE-BY",
                "Baden-Württemberg": "DE-BW", "Nordrhein-Westfalen": "DE-NW",
                "Niedersachsen": "DE-NI", "Sachsen": "DE-SN", "Rheinland-Pfalz": "DE-RP",
                "Schleswig-Holstein": "DE-SH", "Brandenburg": "DE-BB", 
                "Sachsen-Anhalt": "DE-ST", "Thüringen": "DE-TH", "Hamburg": "DE-HH",
                "Mecklenburg-Vorpommern": "DE-MV", "Bremen": "DE-HB", "Saarland": "DE-SL"
            }
            
            state_name = address.get('state', '')
            state_code = state_mapping.get(state_name, 'DE-HE') # Default to Hessen if unknown
            city_name = address.get('city', address.get('town', address.get('village', search_query)))

            return {
                "city": city_name,
                "state": state_name,
                "state_code": state_code,
                "lat": float(place['lat']),
                "lon": float(place['lon'])
            }
    except Exception as e:
        print(f"[!] Geo API Error: {e}")
    return None

def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



def get_incident_coordinates(city, district, fallback_lat, fallback_lon):
    """
    Attempts to find exact coordinates for an incident district.
    Uses a small random scatter if the exact street isn't known.
    """
    # Skip generic labels that we know cannot be mapped accurately
    generic_labels = ["City Area", "Major Roads", "Local Area", "Region-wide", "Specific Street / Route"]
    
    if district not in generic_labels:
        
        # SMART ROUTING: If it's a highway (e.g., "A4 Jena"), don't force it into Frankfurt!
        if re.match(r'^A\s?\d+', district):
            query = f"{district}, Germany"
        else:
            # Otherwise, it's a local district like "Ginnheim", so pair it with the city
            query = f"{district}, {city}, Germany"
            
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {'User-Agent': 'Student-Blaulicht-App/2.0'}
        
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data:
                    time.sleep(0.5) # Respect rate limits
                    return float(data[0]['lat']), float(data[0]['lon'])
        except Exception as e:
            pass 
            
    # Fallback: add a tiny random offset from the city center if specific mapping fails
    offset_lat = fallback_lat + random.uniform(-0.025, 0.025)
    offset_lon = fallback_lon + random.uniform(-0.025, 0.025)
    
    return offset_lat, offset_lon