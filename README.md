# Real-Time Blaulicht & Emergency Tracker

A full-stack Python spatial dashboard designed to aggregate and map real-time emergency dispatches, roadblocks, and civil warnings across Germany. 

The system bypasses standard news aggregators by connecting directly to authoritative state-level APIs and RSS feeds. It features a custom algorithmic scoring engine that assesses the driver risk level of live incidents, extracts localized street data, and dynamically plots active hazards on an interactive map.

## Core Architecture
* **Frontend:** Streamlit & Folium (Interactive Web GIS)
* **Backend:** Python (Microservice architecture for API routing)
* **Data Sources:** NINA/MoWaS, Presseportal Polizei, Verkehrsinfo
* **Database:** SQLite (Local persistence for historical data logging)
* **Geocoding:** Nominatim API (OpenStreetMap) with Regex district extraction

## Local Setup
1. Clone the repository: `git clone https://github.com/Code420-dev/Blaulicht-tracker.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the dashboard: `streamlit run app.py`