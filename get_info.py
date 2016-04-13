# get information aout the buildings

import csv
from osgeo import ogr
import json
import configparser
import agd_tools.geo

config = configparser.ConfigParser()
config.read('config.ini')
building_info = config['main']['building_info']
f = open(building_info, 'r')

csvreader = csv.reader(f)

buildings = {}
for row in csvreader:
    ident, geojson, surface, ratio_orientation, orientation = row
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
    surface = float(surface)
    ratio_orientation = float(ratio_orientation)

    buildings[ident] = [ogr_poly, bounding_box, surface, ratio_orientation,
                        orientation]

f.close()

def get_available_ident():
    return buildings.keys()

def get_bounding_box(ident_list):
    bounding_boxes = {}
    for ident in ident_list:
        ogr_poly, bounding_box, surface, ratio_orientation, orientation = buildings[ident]
        bounding_boxes[ident] = bounding_box

    return bounding_boxes

def get_center(ident_list):
    bounding_boxes = {}
    for ident in ident_list:
        ogr_poly, bounding_box, surface, ratio_orientation, orientation = buildings[ident]
        bounding_boxes[ident] = bounding_box

    def compute_center(bounding_box):
        lon_min, lon_max, lat_max, lat_min = bounding_box
        x_min, y_max = agd_tools.geo.geo2carto(lat_min, lon_min)
        x_max, y_min = agd_tools.geo.geo2carto(lat_max, lon_max)

        x_center = (x_min+x_max)/2.
        y_center = (y_min+y_max)/2.

        return x_center, y_center

    return {ident: compute_center(b) for ident, b in bounding_boxes.items()}

def get_orientation(ident_list):
    orientations = {}
    for ident in ident_list:
        ogr_poly, bounding_box, surface, ratio_orientation, orientation = buildings[ident]
        orientations[ident] = orientation
    return orientations
