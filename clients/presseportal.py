import feedparser
import calendar
import time
import re

def get_police_reports(city_name):
    """
    Dynamically fetches live police reports for any specific city.
    """
    short_city = city_name.replace(" am Main", "").replace(" am Rhein", "").strip()
    
    # Dynamic search for local police dispatches
    query = f"(Polizei OR Polizeieinsatz OR Kriminalpolizei) {short_city} -Magazin"
    safe_query = query.replace(" ", "%20")
    url = f"https://news.google.com/rss/search?q={safe_query}&hl=de&gl=DE&ceid=DE:de"
    
    incidents = []
    now_ts = time.time()

    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:10]:
            title = entry.title
            
            # Strict 24-hour filter
            hours_old = 1.0
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_ts = calendar.timegm(entry.published_parsed)
                hours_old = round((now_ts - entry_ts) / 3600, 1)
                
                if hours_old > 24:
                    continue
            
            # Dynamically extract district based on the searched city
            # e.g., looks for "Berlin - Mitte:" instead of just "Frankfurt"
            district = "City Area"
            match = re.search(rf'{short_city}\s*-\s*([^:]+):', title, re.IGNORECASE)
            if match:
                district = match.group(1).strip()
            
            incidents.append({
                "source": f"Polizei {short_city.capitalize()}",
                "category": "Polizei",
                "icon": "🚓",
                "title": title,
                "district": district,
                "hours_old": hours_old,
                "timestamp": entry.published
            })

    except Exception as e:
        print(f"[!] Presseportal API Error: {e}")

    return incidents