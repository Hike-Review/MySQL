#!/bin/bash


curl -X POST -d '{
  "origin":{
    "location":{
      "latLng":{
        "latitude": 37.419734,
        "longitude": -122.0827784
      }
    }
  },
  "destination":{
    "location":{
      "latLng":{
        "latitude": 37.417670,
        "longitude": -122.079595
      }
    }
  },
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE",
  "polylineQuality": "HIGH_QUALITY",
  "departureTime": "2025-10-15T15:01:23.045123456Z",
}' \
-H 'Content-Type: application/json' \
-H 'X-Goog-Api-Key: AIzaSyAD2cbdFh1SlG1240TXmFWDUsKw4OJWdmo' \
-H 'X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline,routes.legs.polyline,routes.legs.steps.polyline' \
'https://routes.googleapis.com/directions/v2:computeRoutes' > scripts/Output.json