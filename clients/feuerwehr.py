import feedparser
import calendar
import time

def get_fire_dispatches(city_name):
    """
    Scans local news radar specifically for recent firefighter deployments,
    strictly limiting to the last 24 hours.
    """
    # Safely clean the city name
    short_city = city_name.replace(" am Main", "").replace(" am Rhein", "").strip()
    
    # Targeted query just for local fires
    query = f"(Feuerwehreinsatz OR Wohnungsbrand OR Feuerwehr) {short_city} -Magazin"
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
                
                # CRITICAL: Drop anything older than 24 hours
                if hours_old > 24:
                    continue

            incidents.append({
                "source": "Local News Radar",
                "category": "Feuerwehr",
                "icon": "🚒",
                "title": title,
                "district": "City Area",
                "hours_old": hours_old,
                "timestamp": entry.published
            })
    except Exception as e:
        print(f"[!] Feuerwehr API Error: {e}")
        
    return incidents