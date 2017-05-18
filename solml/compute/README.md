# compute : apply deep learning on images

## Python files

These files share the names but differ from those in dir train.

* get_info.py : get orientation and position of buildings
* process_batch.py : script that processes a batch

## Data

Extract from OpenStreetMap...

## Notebooks

* batch.ipynb : test the processing of a batch

## Postgresql

`buildings_all.csv` contains the following columns :
* code of the commune (INSEE)
* OpenStreetMap id
* geometry as geojson

Import to postgresql (with postgis) :

```
create table buildings (commune char(5), id_osm bigint, geojson text)
\copy buildings from buildings_all.csv with (format csv, header);
create unique index buildings_id_osm on buildings (id_osm);
alter table buildings add geom geometry;
update buildings set geom = st_setsrid(st_geomfromgeojson(geojson),4326);
create index buildings_geom on buildings using gist(geom);
alter table buildings add merc geometry;
update buildings set merc = st_transform(geom,3857);
alter table buildings add area real;
update buildings set area = st_area(geom::geography);
alter table buildings add convex_hull geometry;
update buildings set convex_hull = st_convexhull(geom);
alter table buildings add convex_hull_carto geometry;
update buildings set convex_hull_carto = st_transform(convex_hull,3857);

```