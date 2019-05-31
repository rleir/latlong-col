#!/usr/bin/env python3
"""
Handy utility to add latlong data to a xls for use in a d3js map.
  read input xls data file
  add lat and long cols
  find the address cols
  google to find the latlongs
  save in the new cols
  write the updated xls
"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from xlrd import open_workbook # type: ignore
from typing import Dict, List
import os
import geopy    # pip install geopy
import geopy.geocoders
from geopy.geocoders import GoogleV3
import json

all_data   = {} # type: Dict
locFileName = 'locations.json'

def readFiles() -> None:
    global all_data
    # read existing locations, zero each count
    with open(locFileName) as json_file:
        all_data = json.load(json_file)
        for addr in all_data:
            all_data[addr]["count"] = 0

    # read xls, find avg sheet
    # path = "../data/revnAcq.xlsx"
    path = "revnAcq.xlsx"
    wb = open_workbook(path)
    s_found    = None
    addrCols   = None
    for sheet in wb.sheets():
        shname = sheet.name
        print("found sheet name "+sheet.name)
        if shname.endswith("Acq xlsx"):
            s_found = 1
            for row in range(sheet.nrows):
                if row == 0:
                    addrCols = getAddressColumns(sheet,row)
                else:
                    getRowAddress(sheet,row,addrCols)
        if s_found is None :
            print("sheet not found in " + path)

def getAddressColumns(sheet,row):
    ''' determine which spreadsheet columns contain address info '''
    cityCol    = None
    provCol    = None
    countryCol = None
    addrCols   = None

    for col in range(sheet.ncols):
        hdr = sheet.cell(row,col).value
        if "City" == hdr :
            cityCol = col
        elif "Prov./state" == hdr :
            provCol = col
        elif "Country" == hdr :
            countryCol = col

        if cityCol is None:
            print(" cityCol not found")
        if provCol is None:
            print(" provCol not found")
        if countryCol is None:
            print(" countryCol not found")
        if cityCol is None and provCol is None and countryCol is None:
            print(" no addr cols found")
        else:
            addrCols = (  cityCol, provCol, countryCol)
    return addrCols

def getRowAddress(sheet,row,addrCols):
    ''' get address info from a spreadsheet row '''
    global all_data
    addr = ""
    for col in range(sheet.ncols):
        if col in addrCols:
            addr += sheet.cell(row,col).value
            addr += ' '
    addr = addr.rstrip() # remove the last space

    if not( addr == ""):
        if addr in all_data.keys():
            all_data[addr]["count"] += 1
        else:
            geo_loc = {}
            geo_loc["count"] = 1
            all_data[ addr] = geo_loc

def getInfo() -> None:
    ''' Google lat lon position for each address '''
    global all_data

    API_KEY = os.getenv("GOOGLEAPI")
    g = GoogleV3(api_key=API_KEY)

    count = 0
    for addr in all_data:
        # if we already have location data, then skip to the next addr
        geo_loc = all_data[ addr]
        if "lat" in geo_loc:
            continue

        location = None
        #addr = "Québec  quebec canada"
        print("addr " + addr)
        try:
            location = g.geocode(addr)
            geo_loc[ "lat" ]    = location.latitude
            geo_loc[ "lon" ]    = location.longitude
            #geo_loc[ "id"  ]    = location.place_id
            geo_loc[ "address" ]= location.address

            all_data[ addr] = geo_loc
            # print( location) # gives  location.address
            # print( location.raw)

            #zzz print(addr[:50] + ' -- ' + location.address)
            print('Lat/Lon: {0}, {1}'.format(location.latitude,location.longitude))
            #zzz print('https://www.google.ca/maps/@{0},{1},17z'.format(location.latitude,location.longitude))
        except (Exception, geopy.exc.GeocoderQueryError) as err:
            print("geopy error: {0}".format(err))
            print('... Failed to get a location for {0}'.format(addr))

        if count == 10:
            return
        count = count+1

def writeFiles() -> None:
    global all_data
    with open(locFileName, 'w', encoding='utf8') as json_file:
        json.dump(all_data, json_file)

if __name__ == "__main__":
# execute only if run as a script

    readFiles()
    getInfo()
    writeFiles()

    


