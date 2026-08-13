import requests

def fetch_live_warnings():
    print("Fetching live emergency data from the German Federal Warning System (NINA)...")
    
    url = "https://warnung.bund.de/api31/mowas/mapData.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        warnings = response.json()
        
        print(f"\n[+] Found {len(warnings)} active warnings nationwide.")
        print("Scanning for local alerts in Hessen / Frankfurt am Main...\n")
        
        local_found = False
        
        for warning in warnings:
            # 
            warning_id = warning.get('id', '')
            severity = warning.get('severity', 'Unknown')
            
            # 2. Safely dig into the nested translation dictionary for the German title
            title_dict = warning.get('i18nTitle', {})
            headline = title_dict.get('de', 'No details provided')
            
            
            
            if 'DE-HE' in warning_id or 'Frankfurt' in headline:
                local_found = True
                print(f"🚨 [LOCAL ALERT DETECTED]")
                print(f"   Severity: {severity}")
                print(f"   Details: {headline}")
                print(f"   Tracking ID: {warning_id}\n")

        
        if not local_found:
            print("✅ No active emergency warnings in the immediate area right now.\n")
            print("Here is a sample of what is happening elsewhere in Germany today:")
            
            for warning in warnings[:2]: 
                warning_id = warning.get('id', 'Unknown ID')
                title_dict = warning.get('i18nTitle', {})
                headline = title_dict.get('de', 'No details provided')
                
                print(f"📍 Region Code: {warning_id[:11]}...") # Print just the location prefix
                print(f"   {headline}\n")

    except requests.exceptions.RequestException as e:
        print(f"[!] Could not connect to the API: {e}")

if __name__ == "__main__":
    fetch_live_warnings()
