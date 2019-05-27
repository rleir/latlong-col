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
import json


all_years = [ ] # type: List[ str]

# Site name keys below match the column headers in the input xlsx
site_keys = [] # type: List[ str]

species_keys = []

all_data   = {} # type: Dict


def readFiles() -> None:
    # read xls, find avg sheet
    # path = "../data/revnAcq.xlsx"
    path = "revnAcq.xlsx"
    wb = open_workbook(path)
    s_found    = None
    #addressCol = None
    cityCol    = None
    provCol    = None
    countryCol = None
    #codeCol    = None
    addrCols   = None
    for sheet in wb.sheets():
        shname = sheet.name
        print("zzz"+sheet.name)
        if shname.endswith("Acq xlsx"):
            s_found = 1
            for row in range(sheet.nrows):
                if row == 0:
                    for col in range(sheet.ncols):
                        hdr = sheet.cell(row,col).value
                        #if "Address" == hdr :
                        #    addressCol = col
                        if "City" == hdr :
                            cityCol = col
                        elif "Prov./state" == hdr :
                            provCol = col
                        elif "Country" == hdr :
                            countryCol = col
                        #elif "Pcode" == hdr :
                        #    codeCol = col

                        #if addressCol is None:
                        #    print(" addrCol not found")
                        if cityCol is None:
                            print(" cityCol not found")
                        if provCol is None:
                            print(" provCol not found")
                        if countryCol is None:
                            print(" countryCol not found")
                        #if codeCol is None:
                        #    print(" codeCol not found")
                        addrCols = (  cityCol, provCol, countryCol)
                        #addrCols = ( addressCol, cityCol, provCol, countryCol, codeCol)
                    else:
                        addr = ""
                        for col in range(sheet.ncols):
                            if col in addrCols:
                                addr += ' '
                                addr += sheet.cell(row,col).value

                        if not addr in all_data.keys():
                            all_data[ addr] = "zzz"
                            print( addr)
    
        if s_found is None :
            print("sheet not found in " + path)


def getInfo() -> None:
    ''' Google lat lon position for each address '''
    for addr in all_data:
        location = None
        try:
            location = g.geocode(addr)
            #        location = g.geocode("O'Reilly Media")
            all_data[ addr] = location
            print(addr[:50] + ' -- ' + location.address)
            print('Lat/Lon: {0}, {1}'.format(location.latitude,location.longitude))
            print('https://www.google.ca/maps/@{0},{1},17z'.format(location.latitude,location.longitude))
        except:
            print('... Failed to get a location for {0}'.format(addr))
        return

def writeFiles() -> None:
    with open('locations.json', 'w') as json_file:
        json.dump(all_data, json_file)

if __name__ == "__main__":
# execute only if run as a script

    readFiles()
    getInfo()
    writeFiles()

    


