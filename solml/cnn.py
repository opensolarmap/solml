import configparser
import pickle
from os.path import dirname, abspath, join, isfile

from keras.applications import VGG16
from keras.optimizers import SGD
import numpy as np

from solml import load


config = configparser.ConfigParser()
config.read('../config.ini')
cnn_cache_dir = config['main']['cnn_cache_dir']

model = VGG16(
    include_top=False,
    weights='imagenet',
    input_tensor=None,
    input_shape=(96, 96, 3),
    pooling=None,
    )
sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss='categorical_crossentropy')


def load_cnn_features(ident):
    filename = cnn_cache_dir + 'cnn_{}.pickle'.format(ident)
    if not isfile(filename):
        return None
    with open(filename, 'rb') as f:
        cnn_feat = pickle.load(f)
    return cnn_feat


def save_cnn_features_list(idents, cnn_features_array):
    for i, ident in enumerate(idents):
        filename = cnn_cache_dir + 'cnn_{}.pickle'.format(ident)
        cnn_feat = cnn_features_array[i]
        with open(filename, 'wb') as f:
            pickle.dump(cnn_feat, f)


def compute_cnn_features_list(idents, bounding_boxes):
    height = 96
    weight = 96
    X = load.load_data(idents, bounding_boxes, weight, height, color=True)

    N = X.shape[0]
    X[:, :, :, 0] -= 103.939
    X[:, :, :, 1] -= 116.779
    X[:, :, :, 2] -= 123.68

    cnn_features = model.predict(X)

    return cnn_features


def get_cnn_features_list(idents, bounding_boxes):
    # Use this fonction from outside

    cnn_features_list = [load_cnn_features(ident) for ident in idents]

    already_computed = [ident for i, ident in enumerate(idents) if cnn_features_list[i] is not None]
    to_compute = [ident for i, ident in enumerate(idents) if cnn_features_list[i] is None]

    if to_compute:
        new_cnn_features_list = compute_cnn_features_list(to_compute, bounding_boxes)
        save_cnn_features_list(to_compute, new_cnn_features_list)
    new_cnn_features_dict = {
        to_compute[i]: new_cnn_features_list[i]
        for i in range(len(to_compute))
    }

    N = len(idents)
    X = np.zeros((N, 4608))
    for i, ident in enumerate(idents):
        if cnn_features_list[i] is not None:
            X[i, :] = cnn_features_list[i].ravel()
        else:
            X[i, :] = new_cnn_features_dict[ident].ravel()

    return X
