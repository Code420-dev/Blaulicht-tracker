import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from clients.nina import get_nina_alerts
from clients.traffic import get_traffic_alerts
from clients.feuerwehr import get_fire_dispatches
from clients.presseportal import get_police_reports
from utils.geo import get_location_info, get_incident_coordinates
from utils.safety import assess_incident
from utils.database import init_db, log_incidents, load_history

# Page Configuration
st.set_page_config(
    page_title="Driver Safety & Route Tracker",
    page_icon="🚘",
    layout="wide"
)

# Initialize the database on startup
init_db()

# PERFORMANCE OPTIMIZATION: CACHING
@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_data(state_code, city_name):
    nina_data = get_nina_alerts(region_code=state_code)
    traffic_data = get_traffic_alerts(state_code, city_name)
    fire_data = get_fire_dispatches(city_name)
    police_data = get_police_reports(city_name)
    return nina_data + traffic_data + fire_data + police_data

st.title("🚘 Live Driver Safety & Route Tracker")
st.markdown("Real-time active emergency deployments, roadblocks, and hazard alerts for drivers across Germany.")

# Sidebar Controls
st.sidebar.header("🔍 Location Settings")
location_input = st.sidebar.text_input("Enter City or Zip Code:", value="Frankfurt am Main")

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Filter Feed")
show_police = st.sidebar.checkbox("🚓 Police (Polizei)", value=True)
show_fire = st.sidebar.checkbox("🚒 Firefighters (Feuerwehr)", value=True)
show_traffic = st.sidebar.checkbox("🚧 Roadblocks & Traffic", value=True)
show_warnings = st.sidebar.checkbox("🚨 Civil Warnings (NINA)", value=True)

if st.sidebar.button("🔄 Force Refresh API Data"):
    fetch_all_data.clear() # Clears the memory cache
    st.rerun()

# Lookup Location Data
location_data = get_location_info(location_input)

if location_data:
    st.sidebar.success(f"📍 Target: **{location_data['city']}** ({location_data['state']})")
    
    with st.spinner("Loading live dispatch data..."):
        
        raw_incidents = fetch_all_data(location_data["state_code"], location_data["city"])

    # Clean, Filter & Score Incidents
    processed_incidents = []
    
    for inc in raw_incidents:
        cat = inc.get('category', 'General')
        
        # Apply sidebar filters BEFORE processing to save speed
        if cat == "Polizei" and not show_police: continue
        if cat == "Feuerwehr" and not show_fire: continue
        if "Road" in cat or "Traffic" in cat or "Closure" in cat:
            if not show_traffic: continue
        if cat == "Emergency Warning" and not show_warnings: continue

        title = inc.get('title', 'No details provided')
        icon = inc.get('icon', '🚨')
        district = inc.get('district', 'Local Area')
        hours_old = inc.get('hours_old', 1.0)
        source = inc.get('source', 'System')
        timestamp = inc.get('timestamp', 'Live')

        safety_status, score = assess_incident(title, cat, hours_old)

        processed_incidents.append({
            "title": title,
            "category": cat,
            "icon": icon,
            "district": district,
            "hours_old": hours_old,
            "source": source,
            "timestamp": timestamp,
            "safety_status": safety_status,
            "score": score
        })

    processed_incidents.sort(key=lambda x: x['score'], reverse=True)

    # Log to our SQLite Database
    log_incidents(processed_incidents)
    
    st.markdown("---")
    
    tab_live, tab_history = st.tabs(["🗺️ Live Map & Active Alerts", "🗄️ Historical Database"])
    
    #  LIVE MAP
    with tab_live:
        st.subheader(f"🗺️ Live Hazard Map for {location_data['city']}")
        
        m = folium.Map(location=[location_data['lat'], location_data['lon']], zoom_start=12)

        for inc in processed_incidents:
            inc_lat, inc_lon = get_incident_coordinates(
                location_data['city'], 
                inc['district'], 
                location_data['lat'], 
                location_data['lon']
            )
            
            if inc['score'] >= 3:
                pin_color = 'red'
            elif inc['score'] >= 2:
                pin_color = 'orange'
            else:
                pin_color = 'blue'

            pin_icon = 'info-sign'
            if 'Feuer' in inc['category']: pin_icon = 'fire'
            elif 'Road' in inc['category'] or 'Traffic' in inc['category'] or 'Closure' in inc['category']: pin_icon = 'road'
            
            popup_html = f"<b>{inc['category']}</b><br><i>{inc['district']}</i><br><br>{inc['safety_status']}"
            
            folium.Marker(
                [inc_lat, inc_lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=inc['title'][:50] + "...",
                icon=folium.Icon(color=pin_color, icon=pin_icon)
            ).add_to(m)

        # returned_objects=[] stops the map from constantly refreshing Streamlit
        st_folium(m, width=1000, height=450, returned_objects=[])

        st.subheader(f"Active Dispatches & Hazards ({len(processed_incidents)} items)")

        if not processed_incidents:
            st.info(f"✅ No major emergency dispatches or roadblocks reported for {location_data['city']} based on your selected filters.")
        else:
            for inc in processed_incidents:
                icon = inc['icon']
                district_tag = f"📍 **Area:** `{inc['district']}`"
                
                if inc['hours_old'] == 0 or inc['hours_old'] < 0.2:
                    age_tag = "🕒 `Just now / Live`"
                else:
                    age_tag = f"🕒 `{inc['hours_old']} hours ago`"

                with st.expander(f"{icon} [{inc['category']}] — {inc['title'][:85]}...", expanded=(inc['score'] >= 2.5)):
                    st.markdown(f"{district_tag} | {age_tag}")
                    st.markdown(f"**Driver Safety Status:** `{inc['safety_status']}`")
                    st.write(f"**Full Details:** {inc['title']}")
                    st.caption(f"Source: {inc['source']} | Published: {inc['timestamp']}")

    # HISTORICAL DATABASE
    with tab_history:
        st.subheader("🗄️ Historical Incident Logs")
        st.markdown("This database logs every emergency event captured during your live scans.")
        
        # Load the data from SQLite and display it as an interactive table
        history_df = load_history()
        
        if not history_df.empty:
            # Display metrics
            st.metric("Total Incidents Logged", len(history_df))
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("The database is currently empty. Wait for active incidents to be scanned.")

else:
    st.sidebar.error("Could not find that location. Please enter a valid German City Name or Zip Code.")
