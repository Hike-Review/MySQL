#!/bin/bash

curl -X POST -d '{
  "origin":{
    "location":{
      "latLng":{
        "latitude": 37.00220800843724,
        "longitude": -122.05563029699175
      }
    }
  },
  "destination":{
    "location":{
      "latLng":{
        "latitude": 37.00222838711686,
        "longitude": -122.05583603275898
      }
    }
  },
  "intermediates": [
    {
      "location":{
        "latLng":{
          "latitude": 37.00691636538292, 
          "longitude": -122.05686782133829
        }
      }
    },
    {    
      "location":{
        "latLng":{
          "latitude": 37.00721699618883,
          "longitude": -122.05651106057233
        }
      }
    },
    {
      "location":{
        "latLng":{
          "latitude": 37.00768330415404, 
          "longitude": -122.06044904072517
        }
      }
    },
    {
      "location":{
        "latLng":{
          "latitude": 37.004204480285736,
          "longitude": -122.05690696998536
        }
      }
    }
  ],
  "travelMode": "WALK",
  "polylineQuality": "HIGH_QUALITY",
  "departureTime": "2025-10-15T15:01:23.045123456Z"
}' \
-H 'Content-Type: application/json' \
-H 'X-Goog-Api-Key: AIzaSyAD2cbdFh1SlG1240TXmFWDUsKw4OJWdmo' \
-H 'X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline,routes.legs.polyline,routes.legs.steps.polyline,routes.legs.startLocation,routes.legs.endLocation' \
'https://routes.googleapis.com/directions/v2:computeRoutes' > bashOutput.json
