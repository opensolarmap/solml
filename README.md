# solml : Machine Learning on roof images

## Directories and modules

Directories:

* `training`: train a model
* `batch`: compute CNN features by batches
* `predict`: use the model on CNN features

Common modules :

* `cnn.py`: use a custom VGG16 CNN
* `download.py`: download building images from mapbox
* `geo.py`: geographic and cartographic functions
* `load.py`: load data, download if not already cached


## Install

First, clone this repository.

Be sure you use python3.

### GDAL

Install GDAL version 2.x. If your favorite package manager does not provide version 2, you can download it from http://download.osgeo.org/gdal/, and then :

```
./configure
make
make install
```

Test the installation with `gdal-config --version`.

Install PROJ4 :

```
apt-get install libproj-dev
```

If pip install GDAL fails, retry after

````
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
````


### PostgreSQL

Install postgresql >= 9.6.

If your favorite package manager does not provide a recent version, follow the instructions in https://www.postgresql.org/download/.

Install also `libpq-dev`.


### Install the python requirements

Make an editable installation.

`pip install -e .`


### Configuration

Copy `config.ini.example` to `config.ini` and adapt it.