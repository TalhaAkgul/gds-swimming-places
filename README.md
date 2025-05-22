# gds-swimming-places
Closest Swimming Spots in Copenhagen

# AquaPath

**SwimPath** is an interactive web application that helps users find the shortest path to the nearest swimming place in Copenhagen. It also visualizes the accessibility of swimming areas through hexagonal isochrone maps for both walking and biking networks.

## Features

- 🌊 Interactive map with clickable locations
- 🏊 View nearest swimming place and its path from any point
- 📍 Display water quality data for each swimming location
- 🧭 Isochrone maps with hexagonal bins showing travel distance
- 🚶🚴 Support for both walking and biking networks

# Technologies Used

- **Frontend:** HTML, JavaScript, Leaflet.js
- **Backend:** Python, Flask
- **Routing & Network Analysis:** OSMnx, NetworkX
- **Data Processing:** Pandas
- **Spatial Analysis:** H3, GeoJSON

## Getting Started

### Prerequisites

Install Python 3.8+ and the following dependencies:

```bash
pip install -r requirements.txt
```
### Run the App
- Make sure graphml file and final_dataset.csv files that ```app.py``` reads are in the root app/ folder.
- ```bash
  python app.py
  ```
### Generating Isochrone Maps
- Make sure graphml file and final_dataset.csv files that ```hexamap.py``` reads are in the root app/ folder.
- ```bash
  python hexamap.py
  ```
 ```copenhagen-hex-boundries.geojson``` has the polygon to fill hexagons with.

### Generating Network Graph
- ```bash
  python cph-map.py
  ```
