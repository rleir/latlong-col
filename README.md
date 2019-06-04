# latlong-col

## Handy utility to add latlong data to a xlsx for use in a d3js map.

The ultimate goal is to add a lat/long column to a spreadsheet, using values from a google search for the pre-existing address info.

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

