import requests

def get_nina_alerts(region_code="DE-HE"):
    """
    Fetches live NINA warnings and returns a standardized list of emergency objects.
    """
    url = "https://warnung.bund.de/api31/mowas/mapData.json"
    incidents = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        warnings = response.json()

        for warning in warnings:
            warning_id = warning.get('id', '')
            title_dict = warning.get('i18nTitle', {})
            headline = title_dict.get('de', 'Keine Details verfügbar')
            severity = warning.get('severity', 'Minor')

            # Filter for region (e.g., DE-HE for Hessen)
            if region_code in warning_id or 'Frankfurt' in headline:
                incidents.append({
                    "id": warning_id,
                    "source": "NINA / MoWaS",
                    "category": "Emergency Warning",
                    "severity": severity,
                    "title": headline,
                    "timestamp": warning.get('startDate', 'N/A')
                })

    except requests.exceptions.RequestException as e:
        print(f"[!] NINA API Error: {e}")

    return incidents