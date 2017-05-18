# solml : Machine Learning on roof images

## Directories and modules

Directories:

* `train`: train a model
* `compute`: compute CNN features by batches
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

#### Troubleshooting

If pip install GDAL fails, retry after

````
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
````

If the package `osgeo` cannot be imported from python, retry after installing `libgeos-dev libwebp-dev unixodbc-dev libxerces-c-dev libjasper-dev libnetcdf-dev libhdf4-alt-dev libgif-dev`.


### PostgreSQL

Install postgresql >= 9.6.

If your favorite package manager does not provide a recent version, follow the instructions in https://www.postgresql.org/download/.

Install also `libpq-dev`.


### Tensorflow

You can install tensorflow from pip and it is the fastest and easiest option.

If you plan to compute the CNN features using a CPU, the packaged version of tensorflow may not take advantage of advanced instruction sets supported by your CPU. In that case tensorflow can be built from source. Tested on CPUs supporting SSE4.1, SSE4.2, AVX, AVX2, FMA (Intel Xeon E5-2643 v3 @ 3.40GHz), the optimized version of tensorflow achieves a 2x speedup compared to the packaged version.

Tensorflow works best on GPUs. Ran on a nVidia GeForce GTX 1060 6Go, a mid to high-end graphic card launched in 2016, tensorflow is 10x faster than on 2 Intel Xeon E5-2643 v3 with the optimiser version. It applies VGG16 on 35.000 images of dimension 96x96 per second. Graphic cards are by far the cheapest and the most efficient option to perform deep learning on large amounts of data.


### Install the python requirements

Make an editable installation.

`pip install -e .`


### Configuration

Copy `config.ini.example` to `config.ini` and adapt it.