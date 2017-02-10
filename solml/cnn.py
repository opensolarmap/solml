import configparser
import pickle
from os.path import dirname, abspath, join, isfile

from keras.models import Sequential
from keras.layers.core import Flatten, Dense, Dropout
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD
import h5py
import numpy as np

from solml import load


config = configparser.ConfigParser()
config.read(join(dirname(abspath(__file__)), 'config.ini'))
cnn_cache_dir = config['main']['cnn_cache_dir']
cnn_weights = config['main']['cnn_weights']


def VGG_16_custom(weights_path):
    model = Sequential()

    model.add(ZeroPadding2D((1, 1), input_shape=(3, 96, 96), dim_ordering='th'))
    model.add(Convolution2D(64, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(64, 3, 3, activation='relu', dim_ordering='th'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), dim_ordering='th'))

    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(128, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(128, 3, 3, activation='relu', dim_ordering='th'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), dim_ordering='th'))

    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(256, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(256, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(256, 3, 3, activation='relu', dim_ordering='th'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), dim_ordering='th'))

    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), dim_ordering='th'))

    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(ZeroPadding2D((1, 1), dim_ordering='th'))
    model.add(Convolution2D(512, 3, 3, activation='relu', dim_ordering='th'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), dim_ordering='th'))

    model.add(Flatten())

    f = h5py.File(weights_path)
    #print(f.attrs['nb_layers'])
    for k in range(32):
        g = f['layer_{}'.format(k)]
        weights = [g['param_{}'.format(p)] for p in range(g.attrs['nb_params'])]
        model.layers[k].set_weights(weights)
    f.close()

    return model

model = VGG_16_custom(cnn_weights)
sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss='categorical_crossentropy')


def load_cnn_features(ident):
    filename = cnn_cache_dir + 'cnn_{}.png'.format(ident)
    if not isfile(filename):
        return None
    with open(filename, 'rb') as f:
        cnn_feat = pickle.load(f)
    return cnn_feat


def save_cnn_features_list(idents, cnn_features_array):
    for i, ident in enumerate(idents):
        filename = cnn_cache_dir + 'cnn_{}.png'.format(ident)
        cnn_feat = cnn_features_array[i, :]
        with open(filename, 'wb') as f:
            pickle.dump(cnn_feat, f)


def compute_cnn_features_list(idents, bounding_boxes):
    data = load.load_data(idents, bounding_boxes, 96, 96, color=True)
    N = data.shape[0]
    X = np.zeros((N, 3, 96, 96))
    for i in range(N):
        im = data[i, :].copy().reshape((96, 96, 3)).copy()
        #plt.imshow(im.astype(np.uint8))
        im[:, :, 0] -= 103.939
        im[:, :, 1] -= 116.779
        im[:, :, 2] -= 123.68
        im = im.transpose((2, 0, 1))
        im = np.expand_dims(im, axis=0)
        X[i, :, :, :] = im
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
        to_compute[i]: new_cnn_features_list[i, :]
        for i in range(len(to_compute))
    }

    N = len(idents)
    X = np.zeros((N, 4608))
    for i, ident in enumerate(idents):
        if cnn_features_list[i]:
            X[i, :] = cnn_features_list[i]
        else:
            X[i, :] = new_cnn_features_dict[ident]

    return X
