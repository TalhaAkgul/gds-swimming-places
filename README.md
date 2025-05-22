# gds-swimming-places
Closest Swimming Spots in Copenhagen

# AquaPath

**AquaPath** is an interactive web application that helps users find the shortest path to the nearest swimming place in Copenhagen. It also visualizes the accessibility of swimming areas through hexagonal isochrone maps for both walking and biking networks.

## Features

- 🌊 Interactive map with clickable locations
- 🏊 View the nearest swimming place and its path from any point
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

Python version: 3.12.

Create a virtual environment
  
```bash
python3 -m venv venv
```

Activate the virtual environment
- On Linux/macOS:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate
```

Install the required packages
```bash
### Generating Network Graph
- If you don't have graphml file, you need to download
- ```bash
  python cph-map.py
  ```
  
### Generating Isochrone Maps
- Make sure graphml file and final_dataset.csv files that ```hexamap.py``` reads are in the root app/ folder.
- ```bash
  python hexamap.py
  ```
 ```copenhagen-hex-boundries.geojson``` has the polygon to fill hexagons with.

 ### Run the App
- Make sure graphml file and final_dataset.csv files that ```app.py``` reads are in the root app/ folder.
- ```bash
  python app.py
  ```
