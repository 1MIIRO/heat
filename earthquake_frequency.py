import os
import shutil
import json
import folium
from folium.plugins import HeatMap, MarkerCluster
from collections import defaultdict

def create_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)  # Delete existing folder
    os.makedirs(folder_name)  # Create a new folder

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_heatmap(json_data, output_folder='output_data', output_file='heatmap.html'):
    # Ensure output folder exists
    create_folder(output_folder)
    output_path = os.path.join(output_folder, output_file)
    
    # Extract data
    locations = [(entry['latitude'], entry['longitude']) for entry in json_data]
    city_data = defaultdict(list)
    
    for entry in json_data:
        city_name = entry.get('city')
        if not city_name:
            continue  # Skip entries without a city
        if isinstance(city_name, list):  # Ensure city name is a string
            city_name = ', '.join([str(c) for c in city_name if c])  # Convert list to string, skipping None values
        city_data[city_name].append(entry)
    
    # Get first and last date for each city
    city_markers = []
    for city, entries in city_data.items():
        lat, lon = entries[0]['latitude'], entries[0]['longitude']
        dates = sorted(entry['date'] for entry in entries)
        first_date, last_date = dates[0], dates[-1]
        city_markers.append((lat, lon, city, first_date, last_date))
    
    # Create map centered around mean location
    avg_lat = sum(lat for lat, lon in locations) / len(locations)
    avg_lon = sum(lon for lat, lon in locations) / len(locations)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)
    
    # Add heatmap layer
    HeatMap(locations).add_to(m)
    
    # Add marker cluster for cities
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, city, first_date, last_date in city_markers:
        popup_content = f"<table border='1'><tr><th>City</th><td>{city}</td></tr>"
        popup_content += f"<tr><th>First Date</th><td>{first_date}</td></tr>"
        popup_content += f"<tr><th>Last Date</th><td>{last_date}</td></tr></table>"
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(marker_cluster)
    
    # Save map
    m.save(output_path)
    print(f"Heatmap saved as {output_path}")

# Example Usage
data_file = 'heat_map\\merged_data.json'  # Ensure this JSON file exists
create_folder('output_data')
data = load_json(data_file)
generate_heatmap(data)
