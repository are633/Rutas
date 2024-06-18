from flask import Flask, request, render_template
import folium
from geopy.geocoders import Nominatim
import googlemaps

app = Flask(__name__)

# Datos de ejemplo
consumo_combustible = 12  # km/l
costo_gasolina = 23.86  # MXN por litro
costo_estimado_peaje = 50  # Costo estimado por cada peaje detectado

# Clave de API de Google Maps (reemplaza con tu propia clave)
gmaps = googlemaps.Client(key='AIzaSyDCdlWcmsljkLcA2fcN3TkvFaUOL4d3tbM')

def geocode_place(place_name):
    geolocator = Nominatim(user_agent="route_finder")
    location = geolocator.geocode(place_name)
    return (location.latitude, location.longitude) if location else None

def get_toll_cost(route):
    total_toll_cost = 0
    if 'legs' in route and 'steps' in route['legs'][0]:
        steps = route['legs'][0]['steps']
        for step in steps:
            if 'html_instructions' in step and 'toll' in step['html_instructions'].lower():
                total_toll_cost += costo_estimado_peaje
    return total_toll_cost

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/route', methods=['POST'])
def route():
    origin_name = request.form['origin']
    destination_name = request.form['destination']

    origin_coords = geocode_place(origin_name)
    destination_coords = geocode_place(destination_name)

    if not origin_coords or not destination_coords:
        return f"Error: no se pudo geocodificar {origin_name if not origin_coords else destination_name}"

    directions_result = gmaps.directions(
        origin=f"{origin_coords[0]},{origin_coords[1]}",
        destination=f"{destination_coords[0]},{destination_coords[1]}",
        mode="driving",
        alternatives=False
    )

    if not directions_result:
        return "Error al obtener la ruta desde la API de Google Maps"

    route = directions_result[0]
    distance_meters = route['legs'][0]['distance']['value']
    distance_km = distance_meters / 1000
    duration_seconds = route['legs'][0]['duration']['value']
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    steps = route['legs'][0]['steps']
    route_coords = [(step['start_location']['lat'], step['start_location']['lng']) for step in steps]
    route_coords.append((steps[-1]['end_location']['lat'], steps[-1]['end_location']['lng']))

    litros_necesarios = distance_km / consumo_combustible
    costo_gasolina_total = litros_necesarios * costo_gasolina
    costo_casetas = get_toll_cost(route)

    m = folium.Map(location=origin_coords, zoom_start=10)
    folium.Marker(location=origin_coords, popup='Origen', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=destination_coords, popup='Destino', icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine(route_coords, color='blue', weight=2.5, opacity=1).add_to(m)

    map_html = m._repr_html_()

    return f"""
    <h2>Ruta más corta de {origin_name} a {destination_name}:</h2>
    <p>Distancia: {distance_km:.2f} km</p>
    <p>Duración: {hours} horas y {minutes} minutos</p>
    <p>Costo de gasolina: ${costo_gasolina_total:.2f} MXN</p>
    <p>Costo de casetas: ${costo_casetas:.2f} MXN</p>
    <p>Costo total estimado: ${costo_gasolina_total + costo_casetas:.2f} MXN</p>
    {map_html}
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
