from clients.nina import get_nina_alerts
from clients.presseportal import get_police_reports

def main():
    print("==================================================")
    print("       REAL-TIME BLAULICHT & EMERGENCY TRACKER    ")
    print("==================================================\n")

    print("[+] Aggregating live incident feeds...")
    
    # 1. Fetch from multiple sources simultaneously
    nina_incidents = get_nina_alerts(region_code="DE-HE")
    police_incidents = get_police_reports()

    # 2. Combine all feeds into one master list
    all_incidents = nina_incidents + police_incidents

    print(f"\n[+] Total Active Incidents Found: {len(all_incidents)}\n")
    print("-" * 50)

    for idx, incident in enumerate(all_incidents, start=1):
        
        icon = "🚓" if "Polizei" in incident['source'] else "🚨"
        
        print(f"[{idx}] {icon} Source  : {incident['source']}")
        print(f"    Category: {incident['category']}")
        print(f"    Severity: {incident['severity']}")
        print(f"    Details : {incident['title']}")
        print(f"    Time    : {incident['timestamp']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
