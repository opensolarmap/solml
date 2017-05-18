# train : train a model on examples

## Python files

* `get_info.py`: get orientation and position of buildings
* `split.py`: load split sets (ids and labels) for training

## Data

This notebooks must be run with the files `contribs.csv` and `buildings.csv` published here: https://www.data.gouv.fr/fr/datasets/donnees-brutes-de-contribution-anonymisees/

These files must be copied to the location `training/contribs_path` and `training/buildings_path` in `config.ini`. 

## Notebooks

* contrib_errors : analysis of contribution errors, mean response time...
* dummy : dummy model
* classif : Logistic Regression (LR) and Support Vector Machines (SVM)
* CNN : use CNN on the roof images
* multi : 4 classes, using CNN and LR. This notebook produces a model saved as `models.pickle`.

