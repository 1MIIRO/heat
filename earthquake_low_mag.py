import os
import shutil
import json
import folium
from folium.plugins import HeatMap, MarkerCluster
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

# Classify Earthquake Magnitudes
def classify_magnitude(magnitude):
    if magnitude <= 2:
        return 'Low_Magnitude'
    elif 3 <= magnitude <= 5:
        return 'Medium_Magnitude'
    elif magnitude >= 5:
        return 'High_Magnitude'
    return None  # If there's no valid data for magnitude

# Convert date string to datetime object for comparison
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Function to add the legend for colors
def add_legend(map_obj):
    legend_html = '''
    <div style="position: fixed; bottom: 30px; left: 30px; width: 180px; height: 230px; background-color: rgba(255, 255, 255, 0.7); z-index:9999; border-radius: 10px; padding: 10px; font-size: 12px;">
        <b>Legend:</b><br>
        <i style="background-color: black; width: 20px; height: 20px; display: inline-block;"></i> Most Frequent<br>
        <i style="background-color: red; width: 20px; height: 20px; display: inline-block;"></i> Least Frequent<br>
        <i style="background-color: orange; width: 20px; height: 20px; display: inline-block;"></i> Highest Magnitude<br>
        <i style="background-color: green; width: 20px; height: 20px; display: inline-block;"></i> Lowest Magnitude<br>
        <i style="background-color: gray; width: 20px; height: 20px; display: inline-block;"></i> Most Current Last Date<br>
        <i style="background-color: blue; width: 20px; height: 20px; display: inline-block;"></i> Least Current Last Date<br>
        <i style="background-color: purple; width: 20px; height: 20px; display: inline-block;"></i> Least Current First Date<br>
        <i style="background-color: white; width: 20px; height: 20px; display: inline-block;"></i> Other Cities<br>
    </div>
    '''
    map_obj.get_root().html.add_child(folium.Element(legend_html))

# Generate a Heatmap and Markers for Low Magnitude Earthquakes
def generate_heatmap(json_data, output_folder='output_data1', output_file='heatmap_low_mag.html'):
    # Ensure output folder exists
    create_folder(output_folder)
    output_path = os.path.join(output_folder, output_file)
    
    # Extract data for heatmap
    low_magnitude_locations = []
    city_data = defaultdict(list)
    low_magnitude_count = defaultdict(int)
    
    # Process each entry in the data
    for entry in json_data:
        latitude = entry['latitude']
        longitude = entry['longitude']
        magnitude = entry['magnitude']
        city_name = entry.get('city')
        date = entry['date']
        
        # Ensure city_name is a string (not a list)
        if isinstance(city_name, list):
            city_name = ', '.join([str(c) for c in city_name if c])  # Join list elements into a string
        
        # Classify earthquake magnitude
        magnitude_type = classify_magnitude(magnitude)
        
        if magnitude_type == 'Low_Magnitude':
            low_magnitude_locations.append((latitude, longitude))
            low_magnitude_count[city_name] += 1  # Count occurrences of Low Magnitude per city
            city_data[city_name].append((latitude, longitude, date, magnitude))
    
    # Calculate the special cities dynamically based on the data
    city_first_date = {}
    city_last_date = {}
    city_max_magnitude = {}
    city_min_magnitude = {}
    
    for city, entries in city_data.items():
        # Sorting entries by date
        dates = sorted(entry[2] for entry in entries)
        first_date, last_date = dates[0], dates[-1]
        max_magnitude = max(entry[3] for entry in entries)
        min_magnitude = min(entry[3] for entry in entries)

        city_first_date[city] = convert_to_datetime(first_date)
        city_last_date[city] = convert_to_datetime(last_date)
        city_max_magnitude[city] = max_magnitude
        city_min_magnitude[city] = min_magnitude
    
    # Get the special cities based on the calculated conditions
    most_frequent_city = max(low_magnitude_count, key=low_magnitude_count.get)
    least_frequent_city = min(low_magnitude_count, key=low_magnitude_count.get)
    highest_magnitude_city = max(city_max_magnitude, key=city_max_magnitude.get)
    lowest_magnitude_city = min(city_min_magnitude, key=city_min_magnitude.get)
    most_current_last_date_city = max(city_last_date, key=city_last_date.get)
    least_current_last_date_city = min(city_last_date, key=city_last_date.get)
    least_current_first_date_city = min(city_first_date, key=city_first_date.get)
    
    # Create map centered around the average latitude and longitude
    avg_lat = np.mean([loc[0] for loc in low_magnitude_locations])
    avg_lon = np.mean([loc[1] for loc in low_magnitude_locations])
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)
    
    # Add heatmap layer for Low Magnitude locations
    HeatMap(low_magnitude_locations).add_to(m)
    
    # Add marker cluster for cities
    marker_cluster = MarkerCluster().add_to(m)

    # Define unique colors for each condition
    color_mapping = {
        "Most Frequent": 'black',
        "Least Frequent": 'red',
        "Highest Magnitude": 'orange',
        "Lowest Magnitude": 'green',
        "Most Current Last Date": 'gray',
        "Least Current Last Date": 'blue',
        "Least Current First Date": 'purple',
        
    }

    # Iterate through the special cities and assign colors
    special_cities = {
        "Most Frequent": most_frequent_city,
        "Least Frequent": least_frequent_city,
        "Highest Magnitude": highest_magnitude_city,
        "Lowest Magnitude": lowest_magnitude_city,
        "Most Current Last Date": most_current_last_date_city,
        "Least Current Last Date": least_current_last_date_city,
        "Least Current First Date": least_current_first_date_city
    }

    # Create markers for special cities
    for condition, city in special_cities.items():
        marker_color = color_mapping.get(condition, 'white')  # Default to white if no match
        
        # Find the city data for the special cities
        city_data_for_marker = city_data.get(city, [])
        
        if city_data_for_marker:
            # Take the first entry for the city
            lat, lon, _, _ = city_data_for_marker[0]
            
            # Add the marker to the map with the assigned color
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(f"City: {city}<br>Condition: {condition}", max_width=300),
                icon=folium.Icon(color=marker_color)
            ).add_to(marker_cluster)

    

    # Add the color legend
    add_legend(m)

    # Save the generated map
    m.save(output_path)
    print(f"Heatmap saved as {output_path}")

# Example Usage
data_file = 'heat_map\\merged_data.json'  # Ensure this JSON file exists
create_folder('output_data1')
data = load_json(data_file)
generate_heatmap(data)
