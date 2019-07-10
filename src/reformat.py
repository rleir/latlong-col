#!/usr/bin/env python3
"""
Handy utility to reformat the locations file for use in a d3js map.
  read input locations data file
  for each location, generate a feature record
  write the features data file
"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from typing import Dict, List
import json

all_data = {}  # type: Dict
fea_data = {}  # type: Dict

# Input locations-with-popup file
locFileName = 'locationsInstitutions.json'

# Output GeoJson file
feaFileName = 'acquisitions.json'


def read_files() -> None:
    global all_data
    # read existing locations, zero each count
    with open(locFileName) as json_file:
        all_data = json.load(json_file)


def reformat_info() -> None:
    ''' generate feature rec with lat lon position for each address '''

    global all_data
    global fea_data
    fea_data["type"] = "FeatureCollection"
    metadata = {}  # some dummy metadata
    metadata["generated"] = 1559586926000   # dummy
    metadata["url"] = "https://zzzz/"       # dummy
    metadata["title"] = "zzz"               # dummy
    metadata["status"] = 200                # dummy
    metadata["api"] = "1.8.1"               # dummy
    metadata["count"] = len(all_data)
    fea_data["metadata"] = metadata

    features = []
    fea_data["features"] = features

    for addr in all_data:
        feature = {}
        properties = {}
        geometry = {}

        if "address" not in all_data[addr]:  # check for key existence
            continue    # skip this record

        properties["place"] = all_data[addr]["address"]
        properties["mag"] = float(all_data[addr]["count"])/10

        if "org names" in all_data[addr]:
            properties["popupContent"] = all_data[addr]["org names"]

        coordinates = []
        coordinates.append(all_data[addr]["lon"])
        coordinates.append(all_data[addr]["lat"])
        coordinates.append(9)
        geometry["type"] = "Point"
        geometry["coordinates"] = coordinates

        feature["type"] = "Feature"
        feature["properties"] = properties
        feature["geometry"] = geometry
        feature["id"] = "zzz"
        features.append(feature)


def write_files() -> None:
    global all_data
    with open(feaFileName, 'w', encoding='utf8') as json_file:
        json.dump(fea_data, json_file)


if __name__ == "__main__":
    # execute only if run as a script

    read_files()
    reformat_info()
    write_files()
