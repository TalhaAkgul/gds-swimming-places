from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import pandas as pd

app = Flask(__name__)

# Load data when the app starts
print("Loading map data...")

""" place_name = "Copenhagen, Denmark"
location = ox.geocode(place_name)
# Get street graph for walking
G = ox.graph_from_point(location, dist=20000, network_type='walk') """

print("Loading saved map graph...")
G = ox.load_graphml("copenhagen_15km.graphml")
print("Graph loaded.")

"""
tags = {"public_transport": "station"}

# Get stations in the area
stations_gdf = ox.features_from_point(location, tags, dist=2000)
stations_gdf = stations_gdf[stations_gdf.geometry.type == "Point"]

# Get street graph for walking
G = ox.graph_from_point(location, dist=2000, network_type='walk')

# Extract coordinates and map them to nearest nodes
target_coords = stations_gdf.geometry.apply(lambda x: (x.y, x.x)).tolist()
target_nodes = [ox.nearest_nodes(G, lon, lat) for lat, lon in target_coords]
"""

df = pd.read_csv("data_cleaning/final_places_and_quality.csv")

# Fix formatting: Replace commas with dots and convert to float
df["Latitude"] = df["Latitude"].str.replace(",", ".").astype(float)
df["Longitude"] = df["Longitude"].str.replace(",", ".").astype(float)

# Optional: Drop rows with missing values (like missing coordinates)
df.dropna(subset=["Latitude", "Longitude"], inplace=True)

# Create station data list with attributes and nearest node
stations = []
for _, row in df.iterrows():
    lat, lon = row["Latitude"], row["Longitude"]
    try:
        node_id = ox.nearest_nodes(G, lon, lat)
        station = {
            "name": row["Name"],
            "latitude": lat,
            "longitude": lon,
            "WaterArea": row.get("WaterArea"),
            "BlueFlag": row.get("BlueFlag"),
            "Good_water": row.get("Good_water"),
            "stofparameter": row.get("Stofparameter"),
            "dato": row.get("Dato"),
            "node_id": node_id
}
        stations.append(station)
    except Exception as e:
        print(f"Skipping station {row['Name']} due to error: {e}")

print(f"Loaded {len(stations)} stations.")
# TODO We can put a button to create a route to an arbitrary station

# Get station coordinates
station_coords = [(s["latitude"], s["longitude"]) for s in stations]

target_nodes = [ox.nearest_nodes(G, lon, lat) for lat, lon in station_coords]

print(f"Loaded {len(target_nodes)} stations.")

@app.route("/")
def index():
    place_name = "Copenhagen, Denmark"
    location = ox.geocode(place_name)

    # Build a larger graph so clicks work better
    G = ox.graph_from_point(location, dist=1000, network_type='walk')
    app.config["graph"] = G  # store for pathfinding

    station_data = []
    for station in stations: #TODO Remove [:10] to get all stations
        # Ensure we only add stations with valid coordinates (latitude and longitude)
        if station["latitude"] and station["longitude"]:
            station_data.append({
            "name": station["name"],
           "lat": station["latitude"],
            "lon": station["longitude"],
            "WaterArea": station.get("WaterArea"),
            "BlueFlag": station.get("BlueFlag"),
            "Good_water": station.get("Good_water"),
            "stofparameter": station.get("stofparameter"),
            "dato": station.get("dato")
})


    app.config["stations"] = station_data  # optional: store for use elsewhere

    return render_template(
        "map.html",
        lat=location[0],
        lon=location[1],
        stations=station_data  # <-- 👈 pass to template
    )
    
@app.route('/shortest-path', methods=['POST'])
def shortest_path():
    data = request.json
    lat, lon = data['lat'], data['lon']
    
    # Store all path lengths
    all_path_lengths = []
    try:
        orig_node = ox.nearest_nodes(G, lon, lat)
    except Exception as e:
        return jsonify({'error': f'Invalid starting location: {str(e)}'}), 400

    # Check if a specific destination was requested
    if "dest_lat" in data and "dest_lon" in data:
        dest_lat = data["dest_lat"]
        dest_lon = data["dest_lon"]
        try:
            dest_node = ox.nearest_nodes(G, dest_lon, dest_lat)
            path = nx.shortest_path(G, orig_node, dest_node, weight='length')
        except Exception as e:
            return jsonify({'error': f'Path to destination failed: {str(e)}'}), 400
    else:
        # Default: find path to the nearest bathing place
        shortest = float('inf')
        path = None
        for station, target_node in zip(stations, target_nodes):
            try:
                candidate_path = nx.shortest_path(G, orig_node, target_node, weight='length')
                length = nx.shortest_path_length(
                G, orig_node, target_node, weight='length')
                all_path_lengths.append({
                'station_name': station['name'],
                'station_lat': station['latitude'],
                'station_lon': station['longitude'],
                'length_meters': length
            })
                if length < shortest:
                        shortest = length
                        path = candidate_path
            except nx.NetworkXNoPath:
                all_path_lengths.append({
                'station_name': station['name'],
                'station_lat': station['latitude'],
                'station_lon': station['longitude'],
                'length_meters': None
            })
            continue

        if not path:
            return jsonify({'error': 'No path found to any bathing place'}), 404

    path_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]
    all_path_lengths = sorted(all_path_lengths, key=lambda x: x['length_meters'] if x['length_meters'] is not None else float('inf'))
    return jsonify({
        'path': path_coords,
        'all_lengths': all_path_lengths
    })


if __name__ == '__main__':
    app.run(debug=True)
