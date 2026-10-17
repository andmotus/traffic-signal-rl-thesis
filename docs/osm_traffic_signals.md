# OpenStreetMap count of traffic-signal nodes

Used in Step 3 of the national scaling model (thesis, Section 3.7). Ingolstadt publishes no count of its signalised intersections, so its number is estimated from OpenStreetMap and calibrated against the official Cologne inventory.

Both queries were run via the Overpass API on **30 August 2026**. They can be rerun in [overpass turbo](https://overpass-turbo.eu).

## Ingolstadt: 558 nodes

```
[out:json];
area["name"="Ingolstadt"]["boundary"="administrative"]["admin_level"="6"]->.searchArea;
node["highway"="traffic_signals"](area.searchArea);
out count;
```

## Cologne: 3,568 nodes

This is the same query, with "Köln" in place of "Ingolstadt":

```
[out:json];
area["name"="Köln"]["boundary"="administrative"]["admin_level"="6"]->.searchArea;
node["highway"="traffic_signals"](area.searchArea);
out count;
```

## How the counts are used

OpenStreetMap puts the `highway=traffic_signals` tag on the junction node or on individual approaches ([OpenStreetMap Wiki](https://wiki.openstreetmap.org/wiki/Tag:highway=traffic_signals)), so a node count is not an intersection count. The Cologne inventory (`lsaknoten_20241031.csv`) lists 964 signalised intersections, which gives 3,568 / 964 = 3.70 nodes per intersection. Dividing Ingolstadt's 558 nodes by this ratio gives an estimate of 151 intersections. The calculation is in `analysis/h4_co2_national.py`.

## Note on reruns

OpenStreetMap is edited continuously, so the counts change over time. Rerun on 17 October 2026 (data as of 20:23 UTC), the Ingolstadt query returned 562 nodes. With that value, and the Cologne count unchanged, the estimate would be 152 intersections instead of 151, and the national estimate would rise by about 0.4%. The analysis and the thesis use the counts of 30 August 2026.

Data © OpenStreetMap contributors, available under the Open Database License (ODbL).
