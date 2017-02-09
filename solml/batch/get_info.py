# get information about the buildings

import csv
from osgeo import ogr
import json
import configparser

import geo

def process_building_info(building_info_filename):
    '''Process csv with columns :
      * INSEE code
      * OSM id
      * geojson

    Return bouding boxes
    '''
    f = open(building_info_filename, 'r')

    csvreader = csv.reader(f)

    buildings = {}
    for row in csvreader:
        insee, ident, geojson = row
        json_poly = json.loads(geojson)
        assert(json_poly['type'] == 'Polygon')
        coordinates = json_poly['coordinates']
        bounding_box_lon_min = min([lon for linear_ring in coordinates for lon, lat in linear_ring])
        bounding_box_lon_max = max([lon for linear_ring in coordinates for lon, lat in linear_ring])
        bounding_box_lat_min = min([lat for linear_ring in coordinates for
                                lon, lat in linear_ring])
        bounding_box_lat_max = max([lat for linear_ring in coordinates for
                                lon, lat in linear_ring])
        bounding_box = [bounding_box_lon_min, bounding_box_lon_max,
                    bounding_box_lat_max, bounding_box_lat_min]
        ogr_poly = ogr.CreateGeometryFromJson(geojson)

        buildings[ident] = bounding_box

    f.close()
    return buildings

def get_available_ident(buildings):
    return list(buildings.keys())

def get_bounding_box(buildings, ident_list):
    return [buildings[ident] for ident in ident_list]

def get_center(buildings, ident_list):
    def compute_center(bounding_box):
        lon_min, lon_max, lat_max, lat_min = bounding_box
        x_min, y_max = agd_tools.geo.geo2carto(lat_min, lon_min)
        x_max, y_min = agd_tools.geo.geo2carto(lat_max, lon_max)

        x_center = (x_min+x_max)/2.
        y_center = (y_min+y_max)/2.

        return x_center, y_center

    return [compute_center(buildings[ident]) for ident in ident_list]

