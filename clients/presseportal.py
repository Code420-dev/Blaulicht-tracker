import feedparser
import re

def get_police_reports():
    """
    Fetches live police dispatch reports and extracts the specific district.
    """
    url = "https://www.presseportal.de/rss/dienststelle_4970.rss2"
    incidents = []

    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:10]:
            title = entry.title
            
            # Extract the specific district from the title using Regex
            # Example: "POL-F: ... Frankfurt - Ginnheim: title" -> extracts "Ginnheim"
            district = "City Area"
            match = re.search(r'Frankfurt\s*-\s*([^:]+):', title)
            if match:
                district = match.group(1).strip()
            
            incidents.append({
                "source": "Polizei Frankfurt",
                "category": "Polizei",
                "icon": "🚓",
                "title": title,
                "district": district,
                "hours_old": 1.0,
                "timestamp": entry.published
            })

    except Exception as e:
        print(f"[!] Presseportal API Error: {e}")

    return incidents