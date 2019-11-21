# latlong-col

[![Build Status](https://travis-ci.com/rleir/latlong-col.svg?branch=master)](https://travis-ci.com/rleir/latlong-col)
[![DeepScan grade](https://deepscan.io/api/teams/5622/projects/7455/branches/75998/badge/grade.svg)](https://deepscan.io/dashboard#view=project&tid=5622&pid=7455&bid=75998)

## Two Sites and a data preparation utility

You will notice some similarities with the connection-map project. Both projects get input information from xlsx spreadsheets and display interactive LeafletJS maps.

Both projects share the locations.json DB. You might want to use filesystem links and make sure you don't run both data utilities simultaneously.

### D3JS spinning globe web graphic

The Nature Museum makes acquisitions worldwide for its collections and to support research. This graphic shows the locations of acquisitons since 1993. The circle size represents the number of acquisitions at that place, on a logarithmic scale.

Since the circles are slightly transparent, overlapping circles add to each other giving a darker shade.


Based on Jeremy Ashkenas's excellent d3 example Quakespotter at

[Observablehq](https://observablehq.com/@jashkenas/quakespotter-0-1@1050)

A difference is that quakespotter displays Richter magnitudes scaling using the Math.exp function. We have values which are best displayed using the math.log function. Also, we divide by 2 not 5.

Files:

*  src/site_spotter/index.html
*  src/site_spotter/inspector.css
*  src/site_spotter/js/quakespotter-0-1.js
*  src/site_spotter/js/inputs.js
*  src/site_spotter/data/acquisitions.geojson

### world-map-with-locations

(this site was previouslyin a separate github project)
The Nature Museum makes acquisitions worldwide for its collections and to support research. This graphic shows the locations of acquisitons since 1993.

The zoomable world map is based on the leaflet.js library with map tiles from OpenStreetMap.

The icons show the locations of institutions. Click on a location to see a popup naming the partner organizations.

The data in GeoJSON format is prepared by the sibling project latlong-col.

Files:

*  src/site_leaf/index.html
*  src/site_leaf/acq.js
*  src/site_leaf/acq-geojson.js - data in GeoJSON format


## Utility to use info from a xlsx, creating a latlong data json file for use in a d3js or leaflet map.

The two sites above use data files prepared by this utility.

Files:

*  src/addLatLong.py

Input:

*  input.xlsx

Outputs from addLatLong.py:

*  locations.json
*  acquisitions.geojson
*  acquisitionsInst.geojson

The goal is to get the lat/long values for locations, for use in the D3 globe. We do a google search using the address info from the spreadsheet. Alternately, the coordinates can be provided in columns labeled Latitude and Longitude, in which case Google will not be consulted.

When Google is being consulted, we save a list of lat/lons in a file locations.json. We don't want to be calling Google every time this program is run, so we keep track of what has already been searched. This locations file is not consulted when the input contains Lat lon columns for the coordinates.

We occasionally experience timeouts from Google, so we have an algorithm which can be run multiple times, each time adding to locations.json.

During development we limit the number of google searches to 10 per run.

You need an API key from Google for use in searches. Store the key in the GOOGLEAPI environment variable before running addLatLong.py .  Before the first run, manually create a null locations.json file.

We should be able to add rows to the xlsx and do another run to get the additional locations.

The column headers do not need to be the first row of the input, but they do need to precede the data. Also, if any rows before the headers contain notes or legends which are similar to a header then there can be confusion .. I.E. a note starting with "City of ..." will be mistaken for the City column header, causing a failed run.

Steps:

*  read locations.json
*  read input xls data file, look for the sheet we need
*  determine which columns contain the address
*  read all rows, saving the address, counting repetitions of an address
*  for each address, google to find the latlongs
*  write the updated locations.json

Bugs

*  The address should be saved in UFT-8
*  The institution name should get saved with the location data
*  Reformat.py should not be a separate script.
