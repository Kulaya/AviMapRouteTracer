import streamlit as st
import folium
from folium.vector_layers import PolyLine
import requests

# Function to get place details using Google Maps API
def get_place_details(lat, lon):
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(url).json()
    if response["results"]:
        return response["results"][0]["formatted_address"]
    return "Unknown Location"

# Function to generate Google Maps shareable link
def generate_google_maps_link(source, destination):
    return f"https://www.google.com/maps/dir/{source}/{destination}"

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

# Initialize session state variables if not already set
if "tracking" not in st.session_state:
    st.session_state.tracking = False
if "source" not in st.session_state:
    st.session_state.source = ""
if "destination" not in st.session_state:
    st.session_state.destination = ""

# Display input fields with session state values
source_coords = st.text_input("Source Coordinates (Auto-detected)", value=st.session_state.source, key="source_input")
destination_coords = st.text_input("Destination Coordinates (Auto-filled on stop)", value=st.session_state.destination, key="destination_input")

# Buttons to control tracking
if st.button("Start Tracking"):
    st.session_state.tracking = True
    st.session_state.source = source_coords  # Store the source when tracking starts
    st.success("Tracking started...")

if st.button("Stop Tracking"):
    st.session_state.tracking = False
    if st.session_state.source:
        st.session_state.destination = source_coords  # Set destination as last tracked point
        st.success("Tracking stopped!")
        google_maps_link = generate_google_maps_link(st.session_state.source, st.session_state.destination)
        st.write("Copy and paste the link below into Google Maps to view your travel path:")
        st.code(google_maps_link)
