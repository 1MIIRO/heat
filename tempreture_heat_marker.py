import os
import shutil
import json
import folium
from folium.plugins import HeatMap
from collections import defaultdict
import numpy as np
from datetime import datetime

# Create a folder to save output
def create_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)  # Delete existing folder
    os.makedirs(folder_name)  # Create a new folder

# Load JSON data from the file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to generate a Temperature Variation Heatmap
def generate_temperature_heatmap(json_data, output_folder='output_data', output_file='temperature_heatmap.html'):
    # Ensure output folder exists
    create_folder(output_folder)
    output_path = os.path.join(output_folder, output_file)
    
    # Extract data for heatmap and to find highest/lowest temperature cities
    temperature_locations = []
    city_temp_data = defaultdict(list)
    highest_temp = -float('inf')
    lowest_temp = float('inf')
    highest_temp_city = ''
    lowest_temp_city = ''
    
    for entry in json_data:
        latitude = entry['latitude']
        longitude = entry['longitude']
        temperature_mean = entry['weather']['temperature_mean']
        
        # Ensure city_name is a string (not a list)
        city_name = entry.get('city')
        if isinstance(city_name, list):
            city_name = ', '.join([str(c) for c in city_name if c])  # Join list elements into a string
        
        # Add temperature data for heatmap
        temperature_locations.append((latitude, longitude, temperature_mean))
        
        # Collect temperature data by city
        city_temp_data[city_name].append(temperature_mean)
        
        # Track highest and lowest temperature
        if temperature_mean > highest_temp:
            highest_temp = temperature_mean
            highest_temp_city = city_name
        
        if temperature_mean < lowest_temp:
            lowest_temp = temperature_mean
            lowest_temp_city = city_name
    
    # Create map centered around the average latitude and longitude
    avg_lat = np.mean([loc[0] for loc in temperature_locations])
    avg_lon = np.mean([loc[1] for loc in temperature_locations])
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)
    
    # Add heatmap layer for temperature mean
    heat_data = [(lat, lon, temp) for lat, lon, temp in temperature_locations]
    HeatMap(heat_data).add_to(m)
    
    # Add markers for cities with highest and lowest temperature mean
    # Highest temperature city - Red marker
    highest_city_data = city_temp_data[highest_temp_city]
    highest_city_lat = np.mean([entry['latitude'] for entry in json_data if entry['city'] == highest_temp_city])
    highest_city_lon = np.mean([entry['longitude'] for entry in json_data if entry['city'] == highest_temp_city])
    folium.Marker(
        [highest_city_lat, highest_city_lon],
        popup=f"City: {highest_temp_city}<br>Temperature: {highest_temp}°C",
        icon=folium.Icon(color='red')
    ).add_to(m)
    
    # Lowest temperature city - Blue marker
    lowest_city_data = city_temp_data[lowest_temp_city]
    lowest_city_lat = np.mean([entry['latitude'] for entry in json_data if entry['city'] == lowest_temp_city])
    lowest_city_lon = np.mean([entry['longitude'] for entry in json_data if entry['city'] == lowest_temp_city])
    folium.Marker(
        [lowest_city_lat, lowest_city_lon],
        popup=f"City: {lowest_temp_city}<br>Temperature: {lowest_temp}°C",
        icon=folium.Icon(color='blue')
    ).add_to(m)

    # Save the generated map
    m.save(output_path)
    print(f"Temperature heatmap saved as {output_path}")

# Example Usage
data_file = 'heat_map\\merged_data.json'  # Ensure this JSON file exists
create_folder('output_data')
data = load_json(data_file)
generate_temperature_heatmap(data)
