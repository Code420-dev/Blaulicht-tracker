import feedparser
import calendar
import time
import re

def extract_district(title, city_name):
    """
    Extracts specific district/street names from German dispatch reports
    e.g. 'POL-F: 260812 - Frankfurt - Alt-Sachsenhausen: ...' -> 'Alt-Sachsenhausen'
    """
    # Pattern to match city name followed by district (e.g., "Frankfurt - Sachsenhausen:")
    pattern = rf"{city_name}\s*(?:am Main)?\s*-\s*([^:]+):"
    match = re.search(pattern, title, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Check if a street/place keyword exists in the title
    if re.search(r'(?:Straße|Str\.|Allee|Weg|Platz|Gasse|Ring|Damm|Brücke|Hauptbahnhof|Autobahn|A\d+)\b', title, re.IGNORECASE):
        return "Specific Street / Route"
        
    return "City-wide / Unspecified"

def scan_local_emergencies(city_name):
    """
    Scans live dispatch feeds and strictly enforces:
    1. Maximum age of 24 hours (drops old news/articles).
    2. Extraction of local neighborhood/district names.
    """
    # Exclude news magazines, search for real-time dispatch reports
    query = f"(Polizei OR Feuerwehr OR Rettungsdienst OR Straßensperrung OR Unfall) {city_name} -Magazin -Zeitung"
    safe_query = query.replace(" ", "%20")
    url = f"https://news.google.com/rss/search?q={safe_query}&hl=de&gl=DE&ceid=DE:de"
    
    incidents = []
    now_ts = time.time()
    
    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # 1. Strict Date Validation
            hours_old = 0
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_ts = calendar.timegm(entry.published_parsed)
                hours_old = round((now_ts - entry_ts) / 3600, 1)
                
                # CRITICAL RULE: Reject anything older than 24 hours!
                if hours_old > 24:
                    continue

            title = entry.title
            
            # 2. Extract District / Location Detail
            district = extract_district(title, city_name)
            
            # 3. Categorize Incident
            if "Feuer" in title or "Brand" in title:
                category = "Feuerwehr"
                icon = "🚒"
            elif "Rettung" in title or "Notarzt" in title:
                category = "Rettungsdienst"
                icon = "🚑"
            elif "Sperrung" in title or "Stau" in title or "Verkehr" in title or "Unfall" in title:
                category = "Verkehr / Roadblock"
                icon = "🚧"
            else:
                category = "Polizei"
                icon = "🚓"

            incidents.append({
                "source": "Live Dispatch Feed",
                "category": category,
                "icon": icon,
                "title": title,
                "district": district,
                "hours_old": hours_old,
                "timestamp": entry.published
            })

    except Exception as e:
        print(f"[!] Scanner Error: {e}")

    return incidents