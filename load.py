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
split_sets = config['main']['split_sets']


def get_sets():
    f = open(split_sets, 'rb')
    train_ids, val_ids, test_ids, train_labels, val_labels, test_labels = pickle.load(f)

    return train_ids, val_ids, test_ids, train_labels, val_labels, test_labels

def split_set(ident_list):
    train_proportion = 0.66
    val_proportion = 0.17
    # test_proportion is implicitely 1-train_proportion-val_proportion

    orientations = get_info.get_orientation(ident_list)

    train_ids = []
    val_ids = []
    test_ids = []
    for class_name in ['1', '2', '3', '4']:
        l = [ident for ident, o in orientations.items() if o == class_name]
        n = len(l)

        np.random.shuffle(l)

        cut1 = int(math.floor(n*train_proportion))
        cut2 = int(math.floor(n*(train_proportion+val_proportion)))
        train_ids += l[:cut1]
        val_ids += l[cut1:cut2]
        test_ids += l[cut2:]

    np.random.shuffle(train_ids)
    np.random.shuffle(val_ids)
    np.random.shuffle(test_ids)

    train_labels = np.array([int(orientations[ident]) for ident in train_ids])
    val_labels = np.array([int(orientations[ident]) for ident in val_ids])
    test_labels = np.array([int(orientations[ident]) for ident in test_ids])

    return train_ids, val_ids, test_ids, train_labels, val_labels, test_labels


def two_balanced_classes():
    N_train = 4000
    N_val = 1000
    N_test = 1000

    ident_list = get_info.get_available_ident()
    orientations = get_info.get_orientation(ident_list)

    l1 = [ident for ident, o in orientations.items() if o == '1']
    l2 = [ident for ident, o in orientations.items() if o == '2']

    np.random.shuffle(l1)
    np.random.shuffle(l2)

    cut1 = int(math.floor(N_train/2))
    cut2 = int(math.floor(N_train/2+N_val/2))
    cut3 = int(math.floor(N_train/2+N_val/2+N_test/2))
    train_ids = l1[:cut1] + l2[:cut1]
    val_ids = l1[cut1: cut2] + l2[cut1: cut2]
    test_ids = l1[cut2: cut3] + l2[cut2: cut3]

    np.random.shuffle(train_ids)
    np.random.shuffle(val_ids)
    np.random.shuffle(test_ids)

    train_labels = np.array([int(orientations[ident]) for ident in train_ids])
    val_labels = np.array([int(orientations[ident]) for ident in val_ids])
    test_labels = np.array([int(orientations[ident]) for ident in test_ids])

    return train_ids, val_ids, test_ids, train_labels, val_labels, test_labels


def load_data(ids, width, height, color):
    N = len(ids)
    if color:
        d = width*height*3
    else:
        d = width*height

    data = np.zeros((N, d))
    for i, ident in enumerate(ids):
        filename = roof_cache_dir + str(ident) + '.jpg'
        if not os.path.isfile(filename):
            download.download([ident])
        image = Image.open(filename)
        resized_image = image.resize((width, height), resample=Image.ANTIALIAS)
        image_data = np.asarray(resized_image, dtype=np.uint8)
        assert image_data.shape == (height, width, 3)
        if color:
            data[i, :] = image_data.ravel()
        else:
            data[i, :] = image_data.mean(axis=2).ravel()
    return data

def load_all_data(train_ids, val_ids, test_ids, l, color):
    width = l
    height = l

    train_data = load_data(train_ids, width, height, color)
    val_data = load_data(val_ids, width, height, color)
    test_data = load_data(test_ids, width, height, color)

    return train_data, val_data, test_data

if __name__ == '__main__':
    ident_list = get_info.get_available_ident()
    train_ids, val_ids, test_ids, train_labels, val_labels, test_labels = split_set(ident_list)

    f = open(split_sets, 'wb')
    pickle.dump([train_ids, val_ids, test_ids, train_labels, val_labels, test_labels], f)
    f.close()
