import feedparser
import calendar
import time
import re

def get_traffic_alerts(state_code, city_name):
    short_city = city_name.replace(" am Main", "").replace(" am Rhein", "").strip()
    
    query = f"(Stau OR Straßensperrung OR Vollsperrung OR Verkehrsunfall) {short_city} -Magazin"
    safe_query = query.replace(" ", "%20")
    url = f"https://news.google.com/rss/search?q={safe_query}&hl=de&gl=DE&ceid=DE:de"
    
    incidents = []
    now_ts = time.time()
    
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            
            hours_old = 1.0
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_ts = calendar.timegm(entry.published_parsed)
                hours_old = round((now_ts - entry_ts) / 3600, 1)
                
                if hours_old > 12:
                    continue

            # NEW: Extract specific Autobahn and nearby city from the title
            district = "Major Roads"
            a_match = re.search(r'\b(A\s?\d+)\b', title)           # Looks for "A4" or "A 5"
            bei_match = re.search(r'bei\s+([A-Z][a-zäöüß]+)', title) # Looks for "bei Jena"
            
            if a_match and bei_match:
                district = f"{a_match.group(1)} {bei_match.group(1)}" # Results in "A4 Jena"
            elif a_match:
                district = a_match.group(1)
            elif bei_match:
                district = bei_match.group(1)
            elif short_city.lower() in title.lower():
                district = short_city

            if "gesperrt" in title.lower() or "sperrung" in title.lower() or "vollsperrung" in title.lower():
                icon = "🚧"
                category = "Active Road Closure"
            else:
                icon = "🚙"
                category = "Traffic Jam / Delay"

            incidents.append({
                "source": "Traffic Radar (Live)",
                "category": category,
                "icon": icon,
                "title": title,
                "district": district, 
                "hours_old": hours_old,
                "timestamp": entry.published
            })
    except Exception as e:
        print(f"[!] Traffic API Error: {e}")
        
    return incidents