# solml : Machine Learning on roof images

## Branches

* master : installation instructions
* training : train a model
* batch : compute CNN features by batches
* predict : use the model on CNN features

## Install

````
sudo apt-get install libgdal-dev python3-gdal libxft-dev
pip install -r requirements.txt
````

if pip install GDAL fails, retry after

````
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
````

Be sure that PROJ4 is installed when running GDAL.

