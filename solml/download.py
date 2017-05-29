# download building images from mapbox

import re
import configparser
from os.path import dirname, abspath, join
import string
import random

from osgeo import gdal, osr, ogr, gdalconst
import numpy as np
from PIL import Image


config = configparser.ConfigParser()
config.read(join(dirname(abspath(__file__)), 'config.ini'))
vrt_url = config['vrt']['url']
vrt_user_agent = config['vrt']['user_agent']
vrt_cache_dir = config['vrt']['cache_dir']
roof_cache_dir = config['main']['roof_cache_dir']


f = open(join(dirname(abspath(__file__)), 'opensolarmap.vrt.template'), 'r')
vrt_template = f.read()
f.close()
vrt_template = vrt_template.replace('%url%', vrt_url)
vrt_template = vrt_template.replace('%user_agent%', vrt_user_agent)
vrt_template = vrt_template.replace('%cache_dir%', vrt_cache_dir)

# randomize to avoid race condition when download.py is imported by parallel jobs
vrt_filename = '/tmp/opensolarmap_{}.vrt'.format(
    ''.join(random.choice(string.ascii_lowercase) for i in range(10)))
f = open(vrt_filename, 'w')
f.write(vrt_template)
f.close()


gdal.UseExceptions()

# Open virtual dataset
dataset = gdal.Open(vrt_filename, gdalconst.GA_ReadOnly)
originX, pixelSizeX, _, originY, _, pixelSizeY = dataset.GetGeoTransform()


# Create coordinates transformation from WGS84 to WebMercator
source = osr.SpatialReference()
source.ImportFromEPSG(4326)     # WGS84
target = osr.SpatialReference()
target.ImportFromEPSG(3857)     # WebMercator
transform_WGS84_to_WebMercator = osr.CoordinateTransformation(source, target)

# Create coordinates transformation from WebMercator to WGS84
source = osr.SpatialReference()
source.ImportFromEPSG(3857)     # WebMercator
target = osr.SpatialReference()
target.ImportFromEPSG(4326)     # WGS84
transform_WebMercator_to_WGS84 = osr.CoordinateTransformation(source, target)


def convert(a_source, b_source, transform):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(a_source, b_source)

    point.Transform(transform)

    point_wkt = point.ExportToWkt()
    a_target, b_target = re.match(r'POINT \((-?[0-9]*\.?[0-9]*) (-?[0-9]*\.?[0-9]*) 0\)',
                    point_wkt).groups()
    a_target = float(a_target)
    b_target = float(b_target)

    return a_target, b_target


def WGS84toWebMercator(lon, lat):
    """Convert from WGS84 to WebMercator."""
    return convert(lon, lat, transform_WGS84_to_WebMercator)


def WebMercatorToWGS84(lon, lat):
    """Convert from WebMercator to WGS84."""
    return convert(lon, lat, transform_WebMercator_to_WGS84)


def coord2pix(x, y):
    """Convert from WebMercator to pixel index."""
    pix_x = int(round((x-originX) / pixelSizeX))
    pix_y = int(round((y-originY) / pixelSizeY))
    return pix_x, pix_y


def pix2coord(x, y):
    """Convert from pixel index to WebMercator."""
    coord_x = originX + pixelSizeX*x
    coord_y = originY + pixelSizeY*y
    return coord_x, coord_y


def fetch_box(west, east, north, south, border):
    """Fetch a box (rectangle) from WGS84 coordinates."""
    assert (west < east)
    assert (north > south)

    x_webmercator_min, y_webmercator_max = WGS84toWebMercator(west, north)
    x_webmercator_max, y_webmercator_min = WGS84toWebMercator(east, south)

    assert (x_webmercator_min < x_webmercator_max)
    assert (y_webmercator_min < y_webmercator_max)

    x_pix_min, y_pix_min = coord2pix(x_webmercator_min, y_webmercator_max)
    x_pix_max, y_pix_max = coord2pix(x_webmercator_max, y_webmercator_min)

    assert (x_pix_min < x_pix_max)
    assert (y_pix_min < y_pix_max)

    # add a border
    x_pix_min -= border
    y_pix_min -= border
    x_pix_max += border
    y_pix_max += border

    size_x = x_pix_max - x_pix_min + 1
    size_y = y_pix_max - y_pix_min + 1

    image = dataset.ReadAsArray(x_pix_min, y_pix_min, size_x, size_y)
    #image = None
    #while image is None:
    #    image = dataset.ReadAsArray(x_pix_min, y_pix_min, size_x, size_y)


    image = np.rollaxis(image, 0, 3)

    return image


def download(ident, bounding_box, border=10):
    filename = roof_cache_dir + ident + '.jpg'

    west, east, north, south = bounding_box
    np_image = fetch_box(west, east, north, south, border)

    pillow_image = Image.fromarray(np_image)

    out_file = open(filename, 'wb')
    pillow_image.save(out_file, 'JPEG')
