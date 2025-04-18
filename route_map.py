import osmnx as ox

# Get walkable network of Copenhagen
G = ox.graph_from_place("Copenhagen, Denmark", network_type="walk")
ox.save_graphml(G, "copenhagen_walk.graphml")
