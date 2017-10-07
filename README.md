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

Install postgresql >= 9.6 and postgis.

If your favorite package manager does not provide a recent version, follow the instructions in https://www.postgresql.org/download/.

Install also `libpq-dev`.

Create a database. Here are a few tips :

* to perform administrative tasks on the database, log in as the postgres user `su postgres`
* to create a database user: `createuser --interactive`
* to create the database `solar`: `createdb solar`
* to edit the access policies : `nano /etc/postgres/9.6/main/pg_hba.conf` (add a line `local solar solar md5`) then reload `systemctl reload postgresql`
* in the `psql` command prompt: (use `\c` to connect, `\l` to list databases and `\d` to list tables)
```
grant all privileges on database solar to solar;
alter user solar with password '***';
\c solar
create extension postgis;
```
* test the connection: `psql solar solar`
* set up a tunnel if your database is not on the same system than the one which runs your python code:
```
ssh -M -S ~/my-ctrl-socket-5432 -fnNT -L 5432:localhost:5432 username@database-machine
ssh -S ~/my-ctrl-socket-5432 -O exit username@database-machine
```


### Tensorflow

You can install tensorflow from pip and it is the fastest and easiest option.

If you plan to compute the CNN features using a CPU, the packaged version of tensorflow may not take advantage of advanced instruction sets supported by your CPU. In that case tensorflow can be built from source. Tested on CPUs supporting SSE4.1, SSE4.2, AVX, AVX2, FMA (Intel Xeon E5-2643 v3 @ 3.40GHz), the optimized version of tensorflow achieves a 2x speedup compared to the packaged version.

Tensorflow works best on GPUs. Ran on a nVidia GeForce GTX 1060 6Go, a mid to high-end graphic card launched in 2016, tensorflow is 10x faster than on 2 Intel Xeon E5-2643 v3 with the optimiser version. It applies VGG16 on 35.000 images of dimension 96x96 per second. Graphic cards are by far the cheapest and the most efficient option to perform deep learning on large amounts of data.


### Install the python requirements

Make an editable installation.

`pip install -e .`


### Configuration

Copy `config.ini.example` to `config.ini` and adapt it.


## Geographic coordinates and cartography

Geographic coordinates are a means to label locations on the earth with numbers. The most used geographic coordinates system nowadays is [WGS84](https://en.wikipedia.org/wiki/World_Geodetic_System). It approximates the surface of the earth as a speroid, and defines a 2-dimensional coordinates system on that theoretical spheroid, composed of a latitude (lat, theta) and a longitude (lon, long, lambda). Although complex, it is possible to compute distances and surfaces using WGS84.

Cartography is the art of representing the surface of the earth on planes, using a "projection". Such a projection cannot be satisfactory as it necessarily violates either angles, distances, surfaces or bearings. Among the huge number of invented projections, [Web Mercator](https://en.wikipedia.org/wiki/Web_Mercator) is commonly used. [Lambert93](https://fr.wikipedia.org/wiki/Projection_conique_conforme_de_Lambert#Projections_officielles_en_France_m.C3.A9tropolitaine) is also commonly used in France. Both Web Mercator and Lambert93 use a 2-dimensional planar system whose axis are called X and Y. Distances and surfaces are fast and easy to compute using Web Mercator or Lambert93 but they are very imprecise.

The Geodetic Parameter Registry assigns a identifier to each of these systems:
* WGS84 : 4326
* Web Mercator : 3857
* Lambert93 : 2154
