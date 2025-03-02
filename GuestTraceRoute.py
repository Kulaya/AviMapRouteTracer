import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.vector_layers import PolyLine
import json
import os

data_file = "route_data.json"

# Function to save route
def save_route(route):
    with open(data_file, "w") as file:
        json.dump(route, file)

# Function to load saved route
def load_route():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return []

# Streamlit UI
st.title("Google Map Route Tracker")

# JavaScript to get real-time geolocation
get_location = """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const location = lat + "," + lon;
            document.getElementById("location").value = location;
        }
    );
    </script>
    <input type="text" id="location" name="location" readonly>
"""

# Display geolocation button
st.components.v1.html(get_location, height=50)

# Get detected location from user input
source = st.text_input("Source (Auto-detected)", key="source")
destination = st.text_input("Enter Destination (Point B)")

# Buttons to control tracking
if "tracking" not in st.session_state:
    st.session_state.tracking = False
    st.session_state.route = []

if st.button("Start Tracking"):
    st.session_state.tracking = True
    st.session_state.route = []
    st.success("Tracking started...")

if st.button("Stop Tracking"):
    st.session_state.tracking = False
    save_route(st.session_state.route)
    st.success("Route saved successfully!")

if st.button("Show Direction"):
    route = load_route()
    if route:
        m = folium.Map(location=route[0], zoom_start=14)
        folium.Marker(route[0], popup="Start (A)", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(route[-1], popup="Destination (B)", icon=folium.Icon(color="red")).add_to(m)
        PolyLine(route, color="blue", weight=5, opacity=0.7).add_to(m)
        folium_static(m)
    else:
        st.error("No saved route found!")
