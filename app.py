from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx

app = Flask(__name__)

# Load data when the app starts
print("Loading map data...")

place_name = "Copenhagen, Denmark"
location = ox.geocode(place_name)
tags = {"public_transport": "station"}

# Get stations in the area
stations_gdf = ox.features_from_point(location, tags, dist=1000)
stations_gdf = stations_gdf[stations_gdf.geometry.type == "Point"]

# Get street graph for walking
G = ox.graph_from_point(location, dist=2000, network_type='walk')

# Extract coordinates and map them to nearest nodes
target_coords = stations_gdf.geometry.apply(lambda x: (x.y, x.x)).tolist()
target_nodes = [ox.nearest_nodes(G, lon, lat) for lat, lon in target_coords]

print(f"Loaded {len(target_nodes)} stations.")

@app.route("/")
def index():
    place_name = "Copenhagen, Denmark"
    location = ox.geocode(place_name)

    # Build a larger graph so clicks work better
    G = ox.graph_from_point(location, dist=1000, network_type='walk')
    app.config["graph"] = G  # store for pathfinding

    # Get metro stations using OSM tags
    tags = {"public_transport": "station"}
    stations_gdf = ox.features.features_from_point(location, tags, dist=1000)

    # Convert stations to a format usable in the HTML template
    station_data = []
    for _, row in stations_gdf.iterrows():
        if row.geometry.geom_type == "Point":
            station_data.append({
                "name": row.get("name", "Unnamed Station"),
                "lat": row.geometry.y,
                "lon": row.geometry.x
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

    try:
        orig_node = ox.nearest_nodes(G, lon, lat)
    except Exception as e:
        return jsonify({'error': f'Invalid starting location: {str(e)}'}), 400

    shortest = float('inf')
    best_path = None
    best_target = None

    for target_node in target_nodes:
        try:
            path = nx.shortest_path(G, orig_node, target_node, weight='length')
            length = nx.shortest_path_length(G, orig_node, target_node, weight='length')
            if length < shortest:
                shortest = length
                best_path = path
                best_target = target_node
        except nx.NetworkXNoPath:
            continue

    if not best_path:
        return jsonify({'error': 'No path found'}), 404

    path_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in best_path]
    return jsonify({'path': path_coords})

if __name__ == '__main__':
    app.run(debug=True)
