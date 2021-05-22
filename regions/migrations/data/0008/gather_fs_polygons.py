#!/usr/bin/env python3
"""
One-time script to gather locations of federal subjects.
"""
import gzip
import json
import os
import sys

from django.contrib.gis.geos import GEOSGeometry
from geopy import geocoders

FS_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '0002')
THIS_DATA_PATH = os.path.dirname(__file__)

GEOCODER_PRECISE_SIMPLIFY_AREA_TO_MAX_POINTS = [
    [0, 200],
    [100, 200],
    [150, 300],
]

NAME_MAP = {
    # http://nominatim.openstreetmap.org/details.php?place_id=172376881
    'Крым': 'Автономная Республика Крым',
}
# https://ru.wikipedia.org/wiki/Субъекты_Российской_Федерации
# MIN_AREA_KM = 800  # Севастополь


def max_points_from_area(geography_area):
    result_points = 0
    for area, points in GEOCODER_PRECISE_SIMPLIFY_AREA_TO_MAX_POINTS:
        if geography_area < area:
            break
        result_points = points
    return result_points


def binary_simplification(geography):

    # http://stackoverflow.com/a/16743805
    # lat [-90, +90]
    # long [-180, +180]
    max_longlat = 200

    target_max = max_points_from_area(geography.area)
    target_from = 0.95 * target_max

    if geography.num_points <= target_max:
        return geography

    gc = geography.simplify(max_longlat, preserve_topology=True)
    if gc.num_points > target_max:  # it's not possible to get less than `target_max` points in this topology
        return gc

    l = 0
    r = max_longlat  # 15 to make Russia contain 144 points - it's the minimum

    while True:
        m = l + (r - l) / 2

        cg = geography.simplify(m, preserve_topology=True)
        if target_from <= cg.num_points <= target_max:  # we are ok with any solution that fits that range
            return cg

        if cg.num_points < target_max:
            r = m
        else:
            l = m


def read_jsonl(line):
    return json.loads(line.replace(r',\N', ',null'))


def search(geocoder, query):
    locations = geocoder.geocode(query, exactly_one=False,
                                 language='ru', geometry='wkt')
    location = max(locations,
                   key=lambda location: GEOSGeometry(location.raw['geotext']).area)
    g = GEOSGeometry(location.raw['geotext'])
    return location, g


def yield_geos():
    geocoder = geocoders.Nominatim(timeout=20, user_agent="vlr-util/0")

    with open(FS_DATA_PATH + '/federal_subject.jsonl', 'rt') as input_jsonl_file:
        for line in input_jsonl_file:
            id, name, kladr_id, okato, type_, type_short, email = read_jsonl(line)

            name = NAME_MAP.get(name, name)

            location, g = search(geocoder, f"{name} {type_}")
            if g.area <= 0.5:  # it's sq degrees or something. definitely not meters/km.
                location, g = search(geocoder, name)

            print([name, location.address, g.geom_type, g.area], file=sys.stderr)
            assert g.geom_type in {'MultiPolygon', 'Polygon'}

            g_simple = binary_simplification(g)
            yield (id, g_simple, )


if __name__ == '__main__':
    with gzip.open(THIS_DATA_PATH + '/federal_subject_with_polygons.jsonl.gz',
                   'wt') as result_jsonl_file:
        for id, g in yield_geos():
            result_jsonl_file.write(json.dumps([id, g.wkt]))
            result_jsonl_file.write('\n')

    # geojson_list = []
    # for id, g in yield_geos():
    #     geojson_list.append(g.json)
    # print('[%s]' % ','.join(geojson_list))
