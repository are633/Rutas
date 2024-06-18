import requests
import folium
origin = (19.594269298497945, -97.77088090563826)
destination = (20.32179420923527, -99.75249148993633)
url = f'http://router.project-osrm.org/route/v1/driving/{origin[1]},{origin[0]};{destination[1]},{destination[0]}?overview=full&geometries=geojson'
response = requests.get(url)

if response.status_code == 200:
    route_data = response.json()
    route_coordinates = route_data['routes'][0]['geometry']['coordinates']
    route_coordinates = [(coord[1], coord[0]) for coord in route_coordinates]
    distance = route_data['routes'][0]['distance'] / 1000
    duration = route_data['routes'][0]['duration'] / 60

    print(f"Distancia: {distance:.2f} km")
    print(f"Duración: {duration:.2f} minutos")
else:
    print(f"Error: {response.status_code}")
    route_coordinates = []

# Crear el mapa centrado en el punto de origen
m = folium.Map(location=origin, zoom_start=10)

# Agregar marcador de origen
folium.Marker(location=origin, popup='Origen', icon=folium.Icon(color='green')).add_to(m)

# Agregar marcador de destino
folium.Marker(location=destination, popup='Destino', icon=folium.Icon(color='red')).add_to(m)

# Agregar la ruta al mapa
if route_coordinates:
    folium.PolyLine(route_coordinates, color='blue', weight=2.5, opacity=1).add_to(m)
# Mostrar el mapa
m