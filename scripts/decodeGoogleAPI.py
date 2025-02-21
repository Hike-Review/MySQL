import googlemaps 
import polyline
import sys
import json
import csv

def decode_polyline(file_in, file_out):
    # Open the input JSON file
    with open(file_in, mode='r', newline='') as infile:
        reader = json.load(infile)

        decoded_points = []
        total_distance = 0
        total_duration = 0  # Store in seconds

        # Extract encoded polyline
        for route in reader.get('routes', []):
            encoded_polyline = route.get('polyline', {}).get('encodedPolyline', '')
            distance = route.get('distanceMeters', 0)
            duration = route.get('duration', "0s")  # Example format: "3404s"

            # Convert duration from "Xs" to integer (seconds)
            duration_seconds = int(duration.replace("s", "")) if duration.endswith("s") else 0

            total_distance += distance
            total_duration += duration_seconds

            if encoded_polyline:
                decoded_points = polyline.decode(encoded_polyline)  # Decode polyline

        # Convert seconds to minutes & hours
        total_duration_minutes = total_duration // 60
        total_duration_hours = total_duration // 3600

        total_distance_miles = total_distance * 0.000621371

        print(f"Total Distance: {total_distance_miles} miles")
        print(f"Total Duration: {total_duration} seconds ({total_duration_minutes} min, {total_duration_hours} hr)")


        # Manually add origin & destination
        origin = (37.0022080084372, -122.055630296991)  # Origin from Bash script, replace these cords for new ones
        destination = (37.0022283871168, -122.055836032758)  # Destination from Bash script, replace these cords for new ones

        # Ensure they are included
        if origin not in decoded_points:
            decoded_points.insert(0, origin)  # Insert at the beginning

        if destination not in decoded_points:
            decoded_points.append(destination)  # Append at the end

        # Write to CSV
        with open(file_out, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Line Number', 'Latitude', 'Longitude'])

            for index, row in enumerate(decoded_points, start=1):# problem is here
                writer.writerow([index] + list(row))
                

# Run the function
file_inn = 'bashOutput.json'
file_outt = 'cordsBuddhaShrineHike.csv' # change name for for file
decode_polyline(file_inn, file_outt)



