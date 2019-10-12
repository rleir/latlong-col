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
# from typing import Dict, List
import os
import geopy    # pip install geopy
import geopy.geocoders
from geopy.geocoders import GoogleV3
import json
from geojsonfile import write_geojson_file

# input xlsx spreadsheet
default_inputfilename = "input.xlsx"

# Input and Output locations file
default_locFileName = 'locations.json'

# Output locations-with-counts file
default_locCountsFilename = 'locationsCounts.json'
default_locCountsGeoJSON = 'acquisitions.geojson'

# Output locations-with-institutions file
default_locInstFilename = 'locationsInstitutions.json'
default_locInstGeoJSON = 'acquisitionsInst.geojson'

INST_DEPT_LABEL = "Inst Dept"
INST_NAME_LABEL = "Inst Name"
warn_blank_cells = False


class AcqInfo:

    all_data = None  # type: Dict
    coords_found_in_xlsx = None

    def __init__(self,
                 locFileName,
                 locCountsFileName,
                 locCountsGeoJSON,
                 locInstFilename,
                 locInstGeoJSON):
        self.locFileName = locFileName
        self.locCountsFileName = locCountsFileName
        self.locCountsGeoJSON = locCountsGeoJSON
        self.locInstFilename = locInstFilename
        self.locInstGeoJSON = locInstGeoJSON

    def scan_spreadsheet(self, xlsx_filename):
        # read xls, find sheets
        wb = open_workbook(xlsx_filename)
        for sheet in wb.sheets():
            addrCols   = None
            orgCols    = None
            coordsCols = None
            for row in range(sheet.nrows):
                # the header row might not be the first one, so
                # try to get get the header row until we find it
                if addrCols is None:
                    addrCols = self.get_address_columns(sheet, row)
                    orgCols = self.get_org_columns(sheet, row)
                    coordsCols = self.get_coords_columns(sheet, row)
                    if coordsCols is not None:
                        self.coords_found_in_xlsx = True
                else:
                    if self.all_data is None:
                        if self.coords_found_in_xlsx is not None:
                            self.all_data = {}
                        else:
                            # read existing locations DB
                            with open(self.locFileName) as json_file:
                                self.all_data = json.load(json_file)

                                # init the reference counting
                                for addr in self.all_data:
                                    self.all_data[addr]["magnitude"] = 0

                    addr = self.get_row_address(sheet, row, addrCols)
                    if not(addr == ""):
                        self.save_row_address(addr)
                        # add the Institution names
                        if orgCols is not None:
                            orgName = self.get_inst_names(sheet, row, orgCols)
                            self.add_inst_names(addr, orgName)
                    if coordsCols is not None:
                        coords = self.get_row_coords(sheet, row, coordsCols)
                        self.save_row_coords(addr, coords)

        # get any latlong info
        if coordsCols is None:
            self.get_info()

        # write augmented data including insti names to a file
        self.write_loc_inst_file()

        # remove insti name information
        self.remove_inst_element()

        # write basic location count data to a file
        self.write_loc_counts_file()

    def get_address_columns(self, sheet, row):
        ''' determine which spreadsheet columns contain address info '''
        locaCol    = None
        cityCol    = None
        provCol    = None
        countryCol = None
        addrCols   = None

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            try:
                if "Location" == hdr:
                    locaCol = col
                elif hdr.startswith("City"):
                    cityCol = col
                elif "Prov./state" == hdr:
                    provCol = col
                elif "Province" == hdr:
                    provCol = col
                elif "Country" == hdr:
                    countryCol = col
            except AttributeError:
                print("looking for a col header, but cell value is ", hdr)

            if warn_blank_cells:
                if cityCol is None:
                    print(" cityCol not found")
                if provCol is None:
                    print(" provCol not found")
                if countryCol is None:
                    print(" countryCol not found")

            if cityCol is None and provCol is None and countryCol is None:
                if warn_blank_cells:
                    print(" no addr cols found")
            else:
                addrCols = (locaCol, cityCol,  provCol,  countryCol)
        return addrCols

    def get_org_columns(self, sheet, row):
        ''' determine which spreadsheet cols contain organization name info '''
        deptCol = None
        nameCol = None
        orgCols = None

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            if INST_DEPT_LABEL == hdr:
                deptCol = col
            elif INST_NAME_LABEL == hdr:
                nameCol = col

            if warn_blank_cells:
                if deptCol is None:
                    print(" org dept Col not found")
                if nameCol is None:
                    print(" org name Col not found")

            if deptCol is None and nameCol is None:
                if warn_blank_cells:
                    print(" no org cols found")
            else:
                orgCols = (deptCol, nameCol)
        return orgCols

    def get_coords_columns(self, sheet, row):
        ''' determine which spreadsheet cols contain lat lon info '''
        latCol     = None
        lonCol     = None
        coordsCols = None

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            if "Latitude" == hdr:
                latCol = col
            elif "Longitude" == hdr:
                lonCol = col

        if latCol is None or lonCol is None:
            if warn_blank_cells:
                print(" no coords cols found")
        else:
            coordsCols = (latCol, lonCol)
        return coordsCols

    def get_row_address(self, sheet, row, addrCols):
        ''' get address info from a spreadsheet row '''
        addr = ""

        try:
            for col in range(sheet.ncols):
                if col in addrCols:
                    cellval = sheet.cell(row, col).value
                    addr += cellval
                    addr += ' '
        except TypeError:
            print("looking for an address string, but cell value is ", cellval)

        addr = addr.rstrip()  # remove the last space
        addr = addr.lstrip()  # remove any leading spaces
        return addr

    def save_row_address(self, addr):
        '''make sure we have a record for addr and count references to it'''

        if addr == "":
            return
        if addr.startswith("various"):
            return
        if addr.startswith("unknown"):
            return

        if addr in self.all_data.keys():
            try:
                self.all_data[addr]["magnitude"] += 1
            except (Exception,  KeyError) as err:
                print("missing addr entry: {0}".format(err))
                print(addr)

        else:
            geo_loc = {}
            geo_loc["magnitude"] = 1
            geo_loc["org names"] = []
            self.all_data[addr] = geo_loc

    def get_inst_names(self, sheet, row, orgCols):
        ''' get address info from a spreadsheet row '''
        orgName = ""
        orgInst = ""
        orgDept = ""

        for col in range(sheet.ncols):
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
        return orgName

    def get_row_coords(self, sheet, row, coordsCols):
        ''' get coords info from a spreadsheet row '''
        (latCol, lonCol) = coordsCols
        latVal = None
        lonVal = None

        for col in range(sheet.ncols):
            if col == latCol:
                latVal = sheet.cell(row, col).value
            elif col == lonCol:
                lonVal = sheet.cell(row, col).value
        return (latVal, lonVal)

    def add_inst_names(self, addr,  orgName):
        # Do not show anything starting with 'Estate ',
        #   for privacy: it will be followed by a person's name
        if orgName.startswith("Estate "):
            orgName = ""

        # Do not show anything with the Inst = "Canadian Museum of Nature"
        #   we want to know where the acquisition was from,
        #   and this record does not tell us
        if orgName.endswith("Canadian Museum of Nature"):
            orgName = ""

        if not(addr in self.all_data.keys()):
            if addr != "":
                print("===addr not found " + addr)
        else:
            if "org names" not in self.all_data[addr].keys():
                self.all_data[addr]["org names"] = {orgName: 1}
            else:
                if orgName in self.all_data[addr]["org names"]:
                    self.all_data[addr]["org names"][orgName] += 1
                else:
                    try:
                        self.all_data[addr]["org names"][orgName] = 1
                    except (Exception,  TypeError) as err:
                        print("missing orgname entry: {0}".format(err))
                        print(addr)

    def save_row_coords(self, addr, coords):
        (latVal, lonVal) = coords

        if not(addr in self.all_data.keys()):
            if addr != "":
                print("===addr not found " + addr)
        else:
            # In this case, coords do not come from the locations db,
            #   they come from the xlsx row.
            geo_loc = {}
            geo_loc["magnitude"] = 1
            geo_loc["latitude"]  = latVal
            geo_loc["longitude"] = lonVal
            self.all_data[addr] = geo_loc

    def get_info(self) -> None:
        ''' Google lat lon position for each address '''

        g = None
        gcount = 0
        for addr in self.all_data:
            if addr.startswith("various"):
                continue
            elif addr.startswith("unknown"):
                continue

            # if we already have location data, then skip to the next addr
            geo_loc = self.all_data[addr]
            if "latitude" in geo_loc:
                continue

            print(addr)
            if g is None:
                API_KEY = os.getenv("GOOGLEAPI")
                g = GoogleV3(api_key=API_KEY)

            location = None

            try:
                location = g.geocode(addr)
                geo_loc["latitude"]  = location.latitude
                geo_loc["longitude"] = location.longitude
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

            # limit the number of google lookups per run
            if gcount >= 10:
                return
            gcount = gcount+1

    # remove all the "org names" elements
    def remove_inst_element(self):
        for i, (k, v) in enumerate(self.all_data.items()):
            v.pop("org names", None)

    def write_loc_counts_file(self):
        # still write the old files
        # write the trad counts output file
        filename = self.locCountsFileName
        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(self.all_data, json_file)

        filename = self.locCountsGeoJSON
        write_geojson_file(self.all_data, filename, and_properties=False)

    def write_loc_inst_file(self):

        # still write the old files
        # write the trad inst output file
        filename = self.locInstFilename
        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(self.all_data, json_file)

        filename = self.locInstGeoJSON
        write_geojson_file(self.all_data, filename, and_properties=True)

    def write_location_DB(self):
        # if we did not use the locations DB, then do not update it
        if self.coords_found_in_xlsx is not None:
            return

        # remove the location counts and Inst names
        for addr in self.all_data:
            # remove orgname key and its entries (a missing key is OK)
            self.all_data[addr].pop('org names', None)

            # remove magnitude key (will raise KeyError for missing key)
            try:
                self.all_data[addr].pop('magnitude')
            except (Exception,  KeyError) as err:
                print("missing mag entry: {0}".format(err))

        # update the location DB file
        filename = self.locFileName
        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(self.all_data, json_file)


if __name__ == "__main__":
    # execute only if run as a script

    a1 = AcqInfo(default_locFileName,
                 default_locCountsFilename,
                 default_locCountsGeoJSON,
                 default_locInstFilename,
                 default_locInstGeoJSON)

    a1.scan_spreadsheet(default_inputfilename)

    a1.write_location_DB()
