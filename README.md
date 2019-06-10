# latlong-col

## D3JS spinning globe web graphic

The Nature Museum makes acquisitions worldwide for its collections and to support research. This graphic shows the locations of acquisitons since 1993. The circle size represents the number of acquisitions at that place, on a logarithmic scale.

Since the circles are slightly transparent, overlapping circles add to each other giving a darker shade.


Based on Jeremy Ashkenas's excellent d3 example Quakespotter at

  https://observablehq.com/@jashkenas/quakespotter-0-1@1050

A difference is that quakespotter displays Richter magnitudes scaling using the Math.exp function. We have values which are best displayed using the math.log function. Also, we divide by 2 not 5.

Files:

  index.html
  inspector.css
  js/quakespotter-0-1.js
  js/inputs.js
  data/acquisitions.geojson

## Handy utility to add latlong data to a xlsx for use in a d3js map.

Files:

  addLatLong.py
  reformat.py

Input:

  revnAcq.xlsx

Output:

  locations.json


The goal is to get the lat/long values for locations, for use in the D3 globe. We do a google search using the address info from the spreadsheet.

As a stepping stone towards that, we read the xlsx and build a list of lat/lons in a file locations.json. We don't want to be calling Google multiple times for the same location, so we keep track of what has already been done.

We occasionally get timeouts from Google, so we have an algorithm which can be run multiple times, each time adding to locations.json.

During development we limit the number of google searches to 10 per run.

You need an API key from Google for use in searches. Store the key in the GOOGLEAPI environment variable before running addLatLong.py .  Before the first run, manually create a null locations.json file.

We should be able to add rows to the xlsx and do another run to get the additional locations.

Steps:

  read locations.json
  read input xls data file, look for the sheet we need
  determine which columns contain the address
  read all rows, saving the address, counting repetitions of an address
  for each address, google to find the latlongs
  write the updated locations.json

Bugs

  The address should be saved in UFT-8
  The institution name should get saved with the location data
