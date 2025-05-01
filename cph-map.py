import osmnx as ox

# Only run this once to save the graph
place_name = "Copenhagen, Denmark"
location = ox.geocode(place_name)

print("Downloading graph...")
G = ox.graph_from_point(location, dist=15000, network_type='walk')
ox.save_graphml(G, "copenhagen_15km.graphml")
