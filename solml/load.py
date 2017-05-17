# load.py : load data, download if not already cached

import configparser
from os.path import dirname, abspath, join, isfile

import numpy as np
from PIL import Image

from solml import download


config = configparser.ConfigParser()
config.read(join(dirname(abspath(__file__)), 'config.ini'))
roof_cache_dir = config['main']['roof_cache_dir']


def load_data(ids, bounding_boxes, width, height, color):
    N = len(ids)
    if color:
        n_channel = 3
    else:
        n_channel = 1

    data = np.zeros((N, height, width, n_channel))
    for i, ident in enumerate(ids):
        filename = roof_cache_dir + str(ident) + '.jpg'
        if not isfile(filename):
            download.download(ident, bounding_boxes[ident])
        image = Image.open(filename)
        resized_image = image.resize((width, height), resample=Image.ANTIALIAS)
        image_data = np.asarray(resized_image, dtype=np.uint8)
        assert image_data.shape == (height, width, 3)
        if color:
            data[i, :, :, :] = image_data
        else:
            data[i, :, :, 0] = image_data.mean(axis=2)
    return data
