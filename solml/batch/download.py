# download building images from mapbox

from osgeo import gdal
from osgeo import osr
from osgeo import ogr
import osgeo.gdalconst
import re
import numpy as np
from PIL import Image
import configparser

import get_info

config = configparser.ConfigParser()
config.read('config.ini')
mapbox_token = config['mapbox']['token']
mapbox_cache_dir = config['mapbox']['cache_dir']
roof_cache_dir = config['main']['roof_cache_dir']

#f = open('mapbox.vrt.template', 'r')
#vrt_template = f.read()
#f.close()
#vrt_template = vrt_template.replace('%token%', mapbox_token)
#vrt_template = vrt_template.replace('%cache_dir%', mapbox_cache_dir)
#f = open('mapbox.vrt', 'w')
#f.write(vrt_template)
#f.close()


gdal.UseExceptions()

# Open virtual dataset
dataset = gdal.Open('mapbox.vrt', osgeo.gdalconst.GA_ReadOnly)
originX, pixelSizeX, _, originY, _, pixelSizeY = dataset.GetGeoTransform()


# Create coordinates transformation from WGS84 to WebMercator
source = osr.SpatialReference()
source.ImportFromEPSG(4326)     # WGS84
target = osr.SpatialReference()
target.ImportFromEPSG(3857)     # WebMercator
transform = osr.CoordinateTransformation(source, target)


def WGS84toWebMercator(lon, lat):
    """Convert from WGS84 to WebMercator."""
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)

    point.Transform(transform)

    point_wkt = point.ExportToWkt()
    x, y = re.match(r'POINT \((-?[0-9]*\.?[0-9]*) (-?[0-9]*\.?[0-9]*) 0\)',
                    point_wkt).groups()
    x = float(x)
    y = float(y)

    return x, y


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


def fetch_box(left, right, up, down):
    """Fetch a box (rectangle) from WGS84 coordinates."""
    assert (left < right)
    assert (up > down)

    x_webmercator_min, y_webmercator_max = WGS84toWebMercator(left, up)
    x_webmercator_max, y_webmercator_min = WGS84toWebMercator(right, down)

    assert (x_webmercator_min < x_webmercator_max)
    assert (y_webmercator_min < y_webmercator_max)

    x_pix_min, y_pix_min = coord2pix(x_webmercator_min, y_webmercator_max)
    x_pix_max, y_pix_max = coord2pix(x_webmercator_max, y_webmercator_min)

    assert (x_pix_min < x_pix_max)
    assert (y_pix_min < y_pix_max)

    # add a border
    x_pix_min -= 10
    y_pix_min -= 10
    x_pix_max += 10
    y_pix_max += 10

    size_x = x_pix_max - x_pix_min + 1
    size_y = y_pix_max - y_pix_min + 1

    image = None
    while image is None:
        image = dataset.ReadAsArray(x_pix_min, y_pix_min, size_x, size_y)
    image = np.rollaxis(image, 0, 3)

    return image


def download(buildings, ident_list):
    bounding_boxes = get_info.get_bounding_box(buildings, ident_list)

    for ident, bounding_box in zip(ident_list, bounding_boxes):
        filename = roof_cache_dir + ident + '.jpg'

        np_image = fetch_box(*bounding_box)

        pillow_image = Image.fromarray(np_image)

        out_file = open(filename, 'wb')
        pillow_image.save(out_file, 'JPEG')
