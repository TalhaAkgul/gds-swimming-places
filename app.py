import pandas as pd
import osmnx as ox
import networkx as nx
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load map data when the app starts
print("Loading map data...")

place_name = "Copenhagen, Denmark"
location = ox.geocode(place_name)

# Get street graph for walking
G = ox.graph_from_point(location, dist=2000, network_type='walk')

def load_swimming_places(file_path):
    # Load the CSV file instead of an Excel file
    df = pd.read_csv(file_path)
    
    # Extract relevant columns (e.g., coordinates, name) for your swimming places
    swimming_places = df[['nameText', 'lat', 'lon']]  # Update based on your columns
    return swimming_places

swimming_places_file = 'cleaned_DKBW_2022.xlsx'  # This is a CSV file, so the name is misleading
swimming_target_nodes = load_swimming_places(swimming_places_file)

print(f"Loaded {len(swimming_target_nodes)} swimming places.")


@app.route("/")
def index():
    # No need to re-fetch place_name and location here, we already have them loaded globally
    app.config["graph"] = G  # store the graph for pathfinding

    # You can pass the swimming places to the template here
    return render_template(
        "map.html",
        lat=location[0],
        lon=location[1],
        swimming_places=swimming_target_nodes  # pass to template
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

    # Find the nearest swimming place
    for target_node in swimming_target_nodes:
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
