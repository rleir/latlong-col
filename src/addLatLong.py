#!/usr/bin/env python3
"""
Handy utility to add latlong data to a xls for use in a d3js map.
  read input xls data file
  find the address cols
  read the locations file
  google to find any unknown latlongs
  write to the updated locations file
  find the organization name cols from the xls
  get org names, add them to the records
  write a separate file for org names with location

"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from xlrd import open_workbook  # type: ignore
from typing import Dict, List
import os
import geopy    # pip install geopy
import geopy.geocoders
from geopy.geocoders import GoogleV3
import json

# input xlsx spreadsheet
default_inputfilename = "input.xlsx"

# Input and Output locations file
default_locFileName = 'locations.json'

# Output locations-with-popup file
default_locInstFilename = 'locationsInstitutions.json'


INST_DEPT_LABEL = "Inst Dept"
INST_NAME_LABEL = "Inst Name"


class AcqInfo:

    # zzzz locFileName = 'locations.json'
    # zzzz all_data = {}  # type: Dict

    def __init__(self, locFileName, locInstFilename):
        self.locFileName = locFileName
        self.locInstFilename = locInstFilename

        # read existing locations, zero each count
        with open(self.locFileName) as json_file:
            self.all_data = json.load(json_file)
            for addr in self.all_data:
                self.all_data[addr]["count"] = 0

    def scan_spreadsheet(self, xlsx_filename):
        # read xls, find avg sheet
        wb = open_workbook(xlsx_filename)
        s_found    = None
        addrCols   = None
        orgCols    = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("Acq xlsx"):
                s_found = 1
                for row in range(sheet.nrows):
                    if row == 0:
                        addrCols = self.get_address_columns(sheet, row)
                    else:
                        self.get_row_address(sheet, row, addrCols)
                # get any latlong info
                self.get_info()

                # write basic data to a file
                self.write_file(self.locFileName)

                # add the Institution names
                for row in range(sheet.nrows):
                    if row == 0:
                        orgCols  = self.get_org_columns(sheet, row)
                    else:
                        self.add_inst_names(sheet, row, addrCols, orgCols)
                # write augmented data to a different file
                self.write_file(self.locInstFilename)

        if s_found is None:
            print("sheet not found in " + xlsx_filename)

    def get_address_columns(self, sheet, row):
        ''' determine which spreadsheet columns contain address info '''
        cityCol    = None
        provCol    = None
        countryCol = None
        addrCols   = None

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            if "City" == hdr:
                cityCol = col
            elif "Prov./state" == hdr:
                provCol = col
            elif "Country" == hdr:
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
                addrCols = (cityCol,  provCol,  countryCol)
        return addrCols

    def get_org_columns(self, sheet, row):
        ''' determine which spreadsheet cols contain organization name info '''
        deptCol    = None
        nameCol    = None
        orgCols    = None

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            if INST_DEPT_LABEL == hdr:
                deptCol = col
            elif INST_NAME_LABEL == hdr:
                nameCol = col

            if deptCol is None:
                print(" org dept Col not found")
            if nameCol is None:
                print(" org name Col not found")
            if deptCol is None and nameCol is None:
                print(" no org cols found")
            else:
                orgCols = (deptCol, nameCol)
        return orgCols

    def get_row_address(self, sheet, row, addrCols):
        ''' get address info from a spreadsheet row '''
        addr = ""
        for col in range(sheet.ncols):
            if col in addrCols:
                addr += sheet.cell(row, col).value
                addr += ' '
        addr = addr.rstrip()  # remove the last space

        if not(addr == ""):
            if addr in self.all_data.keys():
                self.all_data[addr]["count"] += 1

            else:
                geo_loc = {}
                geo_loc["count"] = 1
                geo_loc["org names"] = []
                self.all_data[addr] = geo_loc

    def add_inst_names(self, sheet,  row,  addrCols,  orgCols):
        ''' get address info from a spreadsheet row '''
        addr = ""
        orgName = ""
        orgInst = ""
        orgDept = ""

        for col in range(sheet.ncols):
            # recreate addr same as we did above
            #    (could use a list and remember it instead)
            if col in addrCols:
                addr += sheet.cell(row, col).value
                addr += ' '

            if col in orgCols:
                if col is orgCols[0]:
                    orgDept = sheet.cell(row, col).value
                    if orgDept != "":
                        orgName += orgDept
                        orgName += ', '
                elif col is orgCols[1]:
                    orgInst = sheet.cell(row, col).value
                    if orgInst != "":
                        orgName += orgInst
        # Do not show anything starting with 'Estate ',
        #   for privacy: it will be followed by a person's name
        if orgName.startswith("Estate "):
            orgName = ""

        # Do not show anything with the Inst = "Canadian Museum of Nature"
        #   we want to know where the acquisition was from,
        #   and this record does not tell us
        if orgInst.startswith("Canadian Museum of Nature"):
            orgName = ""

        addr = addr.rstrip()  # remove the last space
        if not(addr == ""):
            if addr in self.all_data.keys():

                if orgName != "":
                    if "org names" not in self.all_data[addr].keys():
                        self.all_data[addr]["org names"] = {orgName: 1}
                    else:
                        if orgName in self.all_data[addr]["org names"]:
                            self.all_data[addr]["org names"][orgName] += 1
                        else:
                            self.all_data[addr]["org names"][orgName] = 1

            else:
                print("===addr not found " + addr)

    def get_info(self) -> None:
        ''' Google lat lon position for each address '''

        API_KEY = os.getenv("GOOGLEAPI")
        g = GoogleV3(api_key=API_KEY)

        count = 0
        for addr in self.all_data:
            # if we already have location data, then skip to the next addr
            geo_loc = self.all_data[addr]
            if "lat" in geo_loc:
                continue

            location = None

            try:
                location = g.geocode(addr)
                geo_loc["lat"]     = location.latitude
                geo_loc["lon"]     = location.longitude
                # geo_loc["id"]    = location.place_id
                geo_loc["address"] = location.address

                self.all_data[addr] = geo_loc
                # print(location) # gives  location.address
                # print(location.raw)

                # print(addr[:50] + ' -- ' + location.address)
                # print('Lat/Lon: {0}, {1}'
                #       .format(location.latitude,location.longitude))
                # print('https://www.google.ca/maps/@{0},{1},17z'
                #       .format(location.latitude,location.longitude))
            except (Exception,  geopy.exc.GeocoderQueryError) as err:
                print("geopy error: {0}".format(err))
                print('... Failed to get a location for {0}'.format(addr))

            if count == 10:
                return
            count = count+1

    def write_file(self, filename) -> None:
        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(self.all_data, json_file)


if __name__ == "__main__":
    # execute only if run as a script

    a1 = AcqInfo(default_locFileName, default_locInstFilename)

    a1.scan_spreadsheet(default_inputfilename)
