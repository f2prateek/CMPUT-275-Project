from flask import Flask, request, jsonify, render_template
from foursquare import Foursquare
from map import Map
import json

app = Flask(__name__)
app.secret_key = "ZjBjNTUzNWIyMmZmNDRkZGVmYzU5NDY2"

foursquare = Foursquare(client_id='IGJS4FY0IXWLVJVG0IE0IFGIGBVT2HDBK1QAQYMP4WU2VKOE', client_secret='W3SBDEHHTCX2YUSD30Z1RUDIEBJRN3PHTVC0OVBZ0OBGHICK')
graphMap = Map("edmonton-roads-2.0.1.txt")

@app.route("/api/venues")
def api_venues():
    """
    Get a list of venues from Foursquare.
    /venues?location=(44.3,37.2)
    """
    location = eval(request.args.get('location', '(0, 0)'))
    query = request.args.get('query', '')
    
    response = fetch_nearby_foursquare_locations(location, query)
    parsed_response = json.dumps(response)
    return str(parsed_response)

@app.route("/api/route")
def api_route():
    """
    Returns the best route between the given list of locations.

    /route?location=(53.65488,-113.33914)&location=(53.64727,-113.35890)
    /route?location=(53.65488,-113.33914)&location=(53.65035,-113.35026)&location=(53.64727,-113.35890)
    """
    locations = request.values.getlist('location')
    return str(fetch_route(locations))

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/venues")
def venues():
    location = eval(request.args.get('location', '(0, 0)'))
    query = request.args.get('query', '')

    response = fetch_nearby_foursquare_locations(location, query)
    venues = response['venues']
    
    return render_template('venues.html', location=location, venues=venues)

@app.route("/route")
def route():
    """
    tests:
    http://localhost:5000/route?location=(53.51031,-113.50926)&location=(53.49978,-113.50025)
    http://localhost:5000/route?location=(53.51031,-113.50926)&location=(53.49978,-113.50025)&location=(53.50339,-113.50438)
    http://localhost:5000/route?location=(53.51031,-113.50926)&location=(53.49978,-113.50025)&location=(53.50339,-113.50438)&location=(53.50746,-113.50926)
    """
    locations = request.values.getlist('location')
    
    path = fetch_route(locations)

    def process(location):
	return eval(location)
    
    return render_template('route.html', path=path['path'], locations=map(process, locations))

def fetch_route(locations):
    """
    Find an optimized route through the given points.
    Takes in a list of coordinates, each of which is a tuple
    in the format (lat, lng)
    """
    # process the parameters
    points = map(process, locations)
    path = graphMap.find_optimized_path(points)
    path = graphMap.minify_path(path['path'])
    return graphMap.get_path(path)

def fetch_nearby_foursquare_locations(location, query=''):
    """
    Returns nearby location fetched from foursquare.
    Takes in a coordinate, which is a tuple in the format (lat, lng)
    """
    ll = u'' + str(location[0]) + ',' + str(location[1])
    #10km radius
    return foursquare.venues.search(params={'ll': ll, 'intent': 'browse', 'query':query, 'radius':100000})

def process(location):
    """
    Processeses a string containing a coordinate.
    '(53.65488,-113.33914)' >>> (5365488,-11333914)
    """
    location = eval(location)
    return (graphMap.process_coord(location[0]), graphMap.process_coord(location[1]))

def debug(msg):
    """
    Print a debug message.
    """
    app.logger.debug(str(msg))

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run(debug=True)
