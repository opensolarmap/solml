# solml : Machine Learning on roof images

Python files :

These files share the names but differ from those in branch training.

* get_info.py : get orientation and position of buildings
* geo.py : geographic and cartographic functions (extracted from package agd_tools, not used here because of unwanted requirements)
* download.py : download roof images from mapbox
* load.py : load images in memory
* cnn.py : Convolutional Neural Network applied on roof images
* process_batch.py : script that processes a batch

Notebooks :

* batch.ipynb : test the processing of a batch

Other :

* parallel-command : exammple of a use of GNU parallel to process all the batches



