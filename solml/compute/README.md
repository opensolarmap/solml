# compute : apply deep learning on images

## Python files

These files share the names but differ from those in dir train.

* get_info.py : get orientation and position of buildings
* process_batch.py : script that processes a batch

## Data

### Source

`buildings_all.csv` is an extract of all the buildings in france whose surface is >= 100m2 (TODO to be confirmed) contains the following columns :

* code of the commune (INSEE)
* OpenStreetMap id
* geometry as geojson (WGS84)

The request used is:
```
? TODO
```

TODO : surface is computed with WGS84 or WebMercator ? (important for "Collectivités d'outre-mer")

### Import

* create the table that will be used to store all the data about the buildings `create table buildings (commune char(5), id_osm bigint, geojson text);`
* import the data `\copy buildings from /server/var/data/OpenSolarMap/buildings_all.csv with (format csv, header);`
* index by `id_osm` : `create unique index buildings_id_osm on buildings (id_osm);`



Extract from OpenStreetMap...

## Notebooks

* batch.ipynb : test the processing of a batch

## Postgresql

Import to postgresql (with postgis) :

```


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