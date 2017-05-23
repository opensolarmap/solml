import configparser
import math
from io import BytesIO

import psycopg2
import postgis
import numpy as np
from PIL import Image

from solml import download


# Read config

config = configparser.ConfigParser()
config.read(join(dirname(abspath(__file__)), 'config.ini'))
database_host = config['main']['database_host']
database_port = config['main']['database_port']
database_name = config['main']['database_name']
database_username = config['main']['database_username']
database_password = config['main']['database_password']
assert database_host == 'localhost'
assert database_port == '1234'


def compute_angle(convex_hull_carto):
    # Find the rectangle of minimal area covering the building, then compute its angle.
    assert convex_hull_carto.geojson['type'] == 'Polygon'
    assert len(convex_hull_carto.geojson['coordinates']) == 1
    
    rotation_90_degrees = np.array([[0, 1], [-1, 0]])
    
    points = np.array(convex_hull_carto.geojson['coordinates'][0])
    delta = points[1:] - points[:-1]
    distance = np.sqrt(np.power(delta[:,0:1], 2) + np.power(delta[:,1:2], 2))
    tangent = delta/distance
    normal = np.dot(tangent, rotation_90_degrees)
    proj_tangent = np.dot(points, tangent.T)
    proj_normal = np.dot(points, normal.T)
    
    tangent_min = proj_tangent.min(0)
    tangent_max = proj_tangent.max(0)
    normal_min = proj_normal.min(0)
    normal_max = proj_normal.max(0)
    
    length_tangent = tangent_max - tangent_min
    length_normal = normal_max - normal_min
    surface = length_tangent * length_normal
    
    i_orientation = surface.argmin()

    t_min = tangent_min[i_orientation]
    t_max = tangent_max[i_orientation]
    n_min = normal_min[i_orientation]
    n_max = normal_max[i_orientation]
    rectangle_local = np.array([[t_min, n_min], [t_min, n_max], [t_max, n_min], [t_max, n_max]])
    rotation_inverse = np.array([tangent[i_orientation], normal[i_orientation]])
    rectangle = np.dot(rectangle_local, rotation_inverse)
    
    #plt.scatter(rectangle[:,0], rectangle[:,1])
    #plt.scatter(points[:,0], points[:,1])
    #plt.axis('equal')
 
    size_tangent = t_max - t_min
    size_normal = n_max - n_min

    a, b = tangent[i_orientation]
    angle = math.acos(a)
    if b<0:
        angle *= -1
    angle += 2*math.pi
    while angle > math.pi/4.:
        angle -= math.pi/2.

    # angle in rad
    # rectangle in WebMercator
    # size of the rectangle in WebMercator
    return angle, rectangle, (size_normal, size_tangent)


def fetch_image(convex_hull_carto):
    angle, rectangle, size_WebMercator = compute_angle(convex_hull_carto)
   
    west, south = rectangle.min(0)
    east, north = rectangle.max(0)

    west, north = download.WebMercatorToWGS84(west, north)
    east, south = download.WebMercatorToWGS84(east, south)

    original_array = download.fetch_box(west, east, north, south, border=15)
    original_image = Image.fromarray(original_array)
    
    buffer = BytesIO()
    original_image.save(buffer, 'JPEG')
    original_bytes = buffer.getvalue()

    return original_bytes, angle, size_WebMercator


def process_building(nb_worker, id_worker):
    # Open connection
    connection = psycopg2.connect(dbname=database_name, user=database_username, password=database_password)
    cursor = connection.cursor()
    postgis.register(cursor)

    # Fetch the information on one building
    cursor.execute("""
        select id_osm, convex_hull_carto
        from buildings
        sortby commune
        where mod(id_osm, %s)=%s and angle_rad is none
        ;
        """, nb_worker, id_worker)
    data = cursor.fetchall()[0]
    id_osm, convex_hull_carto = data

    # Download and process
    original_bytes, angle, size_WebMercator = fetch_image(convex_hull_carto)

    # Save the data
    cursor.execute("""
        update buildings set
        original_image=%s,
        angle_rad=%s,
        size_WM_X=%s,
        size_WM_Y=%s,
        where id_osm=%s
        ;
        """, original_bytes, angle, size_WebMercator[0], size_WebMercator[1], id_osm)

    cursor.close()
    connection.close()
