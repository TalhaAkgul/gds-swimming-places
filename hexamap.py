import osmnx as ox
import networkx as nx
import pandas as pd
import h3
from shapely.geometry import Polygon
import geopandas as gpd
import json

print("Loading saved map graph...")
# To create hexamap of bike or walk network, you need to graphml files for those networks
G = ox.load_graphml("copenhagen_15km_bike.graphml")
print("Graph loaded.")

df = pd.read_csv("data_cleaning/output/final_dataset.csv")

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
            "Good_water": row.get("Good_water"),
            "stofparameter": row.get("Stofparameter"),
            "dato": row.get("Dato"),
            "node_id": node_id
        }
        stations.append(station)
    except Exception as e:
        print(f"Skipping station {row['Name']} due to error: {e}")

print(f"Loaded {len(stations)} stations.")

# Get station coordinates
station_coords = [(s["latitude"], s["longitude"]) for s in stations]

target_nodes = [ox.nearest_nodes(G, lon, lat) for lat, lon in station_coords]

#Define bounding box or polygon for Copenhagen area
#copenhagen_center = (55.6761, 12.5683) # Copenhagen coordinates
#copenhagen_center = (55.648175, 12.568909)  # Adjusted center
#hex_resolution = 9  # adjust to control hex size
#k_ring = 20  # roughly how far from center to cover

# Generate hexes
#hex_ids = h3.k_ring(h3.geo_to_h3(*copenhagen_center, hex_resolution), k_ring)


# Load GeoJSON
with open("copenhagen-hex-boundries.geojson", "r") as f:
    geojson_data = json.load(f)

# Extract the LineString coordinates
coordinates = geojson_data["features"][0]["geometry"]["coordinates"]

# Convert to Polygon (assumes LineString forms a closed boundary)
polygon = Polygon(coordinates)

# Extract and flip coordinates from (lat, lon) to (lon, lat)
raw_coords = geojson_data["features"][0]["geometry"]["coordinates"]
flipped_coords = [(lon, lat) for lat, lon in raw_coords]

# Create a Polygon
polygon = Polygon(flipped_coords)

# Convert to H3-style GeoJSON polygon format
geo_json_polygon = {
    "type": "Polygon",
    "coordinates": [[list(coord) for coord in polygon.exterior.coords]]
}

# Fill with H3 hexagons at a given resolution
resolution = 9
hex_ids = h3.polyfill(geo_json_polygon, resolution)



print(f"Generated {len(hex_ids)} hexes.")
#stations = stations[:1]  # Limit to first 2 stations for testing
print(f"Len stations: {len(stations)}")
print("Calculating travel times...")


hex_data = []
i=0
print("Running multi-source Dijkstra...")
lengths = nx.multi_source_dijkstra_path_length(
    G, target_nodes, weight="length")
print("Shortest path tree computed.")

# Then in your loop:
for h in hex_ids:
    print("index", i)
    i += 1
    lat, lon = h3.h3_to_geo(h)
    try:
        node = ox.nearest_nodes(G, lon, lat)
        min_dist = lengths.get(node, float('inf'))  # Get distance if reachable
    except:
        print(f"Skipping hex {h} due to error: {e}")
        continue

    hex_boundary = h3.h3_to_geo_boundary(h, geo_json=True)
    polygon = Polygon(hex_boundary)
    hex_data.append({
        'hex': h,
        'geometry': polygon,
        'travel_m': min_dist
    })

# Save to GeoJSON
gdf = gpd.GeoDataFrame(hex_data)
gdf.to_file("static/hex_travel_times_bike.geojson", driver="GeoJSON")
