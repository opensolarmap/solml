# batch : predict by batch

Python files :

These files share the names but differ from those in branch training.

* get_info.py : get orientation and position of buildings
* process_batch.py : script that processes a batch

Notebooks :

* batch.ipynb : test the processing of a batch

Other :

* parallel-command : example of a use of GNU parallel to process all the batches

## Postgresql

`buildings_all.csv` contains the following columns :
* code of the commune (INSEE)
* OpenStreetMap id
* geometry as geojson

Import to postgresql (with postgis) :

```
create table buildings (commune char(5), id_osm bigint, geojson text)
\copy buildings from buildings_all.csv with (format csv, header);
alter table buildings add geom geometry;
update buildings set geom = st_setsrid(st_geomfromgeojson(geojson),4326);
create index buildings_geom on buildings using gist(geom);
```