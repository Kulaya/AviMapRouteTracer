import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.vector_layers import PolyLine
import json
import os
import requests

data_file = "route_data.geojson"

# Function to get place details using Google Maps API
def get_place_details(lat, lon):
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(url).json()
    if response["results"]:
        return response["results"][0]["formatted_address"]
    return "Unknown Location"

# Function to save route in GeoJSON format
def save_route(route):
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in route]
                },
                "properties": {}
            }
        ]
    }
    with open(data_file, "w") as file:
        json.dump(geojson_data, file)

# Function to load saved route
def load_route():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}

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
source_coords = st.text_input("Source Coordinates (Auto-detected)", key="source")
destination_coords = st.text_input("Destination Coordinates (Auto-filled on stop)", key="destination")

# Buttons to control tracking
if "tracking" not in st.session_state:
    st.session_state.tracking = False
    st.session_state.route = []

if st.button("Start Tracking"):
    st.session_state.tracking = True
    st.session_state.route = []
    st.success("Tracking started...")

if st.session_state.tracking:
    current_location = source_coords.split(",")
    if len(current_location) == 2:
        lat, lon = map(float, current_location)
        st.session_state.route.append([lat, lon])
        st.write(f"Current Location: {get_place_details(lat, lon)}")

if st.button("Stop Tracking"):
    st.session_state.tracking = False
    if st.session_state.route:
        save_route(st.session_state.route)
        destination_coords = f"{st.session_state.route[-1][0]},{st.session_state.route[-1][1]}"
        st.session_state.destination = destination_coords
        st.success("Route saved successfully!")

if st.button("Show Direction"):
    route = load_route()
    if route:
        coordinates = route["features"][0]["geometry"]["coordinates"]
        m = folium.Map(location=[coordinates[0][1], coordinates[0][0]], zoom_start=14)
        folium.Marker([coordinates[0][1], coordinates[0][0]], popup="Start (A)", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker([coordinates[-1][1], coordinates[-1][0]], popup="Destination (B)", icon=folium.Icon(color="red")).add_to(m)
        PolyLine([[lat, lon] for lon, lat in coordinates], color="blue", weight=5, opacity=0.7).add_to(m)
        folium_static(m)
    else:
        st.error("No saved route found!")
