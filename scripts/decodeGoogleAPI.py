import googlemaps 
import polyline
import sys
import json
import csv

def decode_polyline(file_in, file_out):
    # Open the input json file for reading
    with open(file_in, mode='r', newline='') as infile:
        # Create a reader object to read from the input file
        reader = json.load(infile)
        
        for route in reader['routes']:
            encoded_polyline = route['polyline']['encodedPolyline']
            # Decode the encoded polyline, which is list of tuples with cords
            decoded_points = polyline.decode(encoded_polyline)
    
        # Open the output CSV file for writing
        with open(file_out, mode='w', newline='') as outfile:
            
            # Create a writer object to write to the output file
            writer = csv.writer(outfile)
            
            # Optional: Write headers to the output file
            writer.writerow(['Line Number', 'Latitude', 'Longitude'])
            
            # Read each row from the input file and write to the output file with a line number
            for index, row in enumerate(decoded_points, start=1):  # start=1 starts numbering from 1
                # Prepend the line number to the row
                writer.writerow([index] + list(row))

# Specify the path to your JSON file
file_inn = 'bashOutput.json'
file_outt = 'pythonOutput.csv'
decode_polyline(file_inn, file_outt)