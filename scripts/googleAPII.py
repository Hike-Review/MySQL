import googlemaps 
import polyline
import sys
import json

'''
API_KEY = "AIzaSyAD2cbdFh1SlG1240TXmFWDUsKw4OJWdmo"

gmaps = googlemaps.Client(key=API_KEY)

orgin = "SantaCruz, CA"
destination = "Scotts Vally, CA"

result = gmaps.directions(orgin, destination)

print(result[0]['legs'][0]['steps']) 
'''

def decode_polyline(file_path):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterate over each route (assuming multiple routes could be in the file)
    for route in data['routes']:
        encoded_polyline = route['polyline']['encodedPolyline']

        # Decode the encoded polyline
        decoded_points = polyline.decode(encoded_polyline)
        print("decoded_points:", len(decoded_points))
        print("Decoded polyline:", decoded_points)

# Specify the path to your JSON file
file_path = 'scripts/Output.json'
decode_polyline(file_path)