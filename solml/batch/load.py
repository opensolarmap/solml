# load data from jpg files

import csv
import numpy as np
import math
from PIL import Image
import pickle
import configparser
import os

import get_info
import download

config = configparser.ConfigParser()
config.read('config.ini')
roof_cache_dir = config['main']['roof_cache_dir']



def load_data(buildings, ids, width, height, color):
    N = len(ids)
    if color:
        d = width*height*3
    else:
        d = width*height

    data = np.zeros((N, d))
    for i, ident in enumerate(ids):
        filename = roof_cache_dir + str(ident) + '.jpg'
        if not os.path.isfile(filename):
            download.download(buildings, [ident])
        image = Image.open(filename)
        resized_image = image.resize((width, height), resample=Image.ANTIALIAS)
        image_data = np.asarray(resized_image, dtype=np.uint8)
        assert image_data.shape == (height, width, 3)
        if color:
            data[i, :] = image_data.ravel()
        else:
            data[i, :] = image_data.mean(axis=2).ravel()
    return data

