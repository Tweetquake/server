from server.earthquake_information import earthquake_faults_finder, risking_area_finder
from osgeo import osr, ogr
from server.geoJSON_creation import geojson_creation
import json
import os

if __name__ == "__main__":
    '''
    example of finding earthquake faults from tweets points
    '''

    with open('server/geoJSON_creation/geojson_data/tweets.geojson', encoding='utf8') as f:
        data = json.load(f)

    points = []
    for feature in (data['features']):
        coord = feature['geometry']['coordinates']
        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(coord[0], coord[1])
        points.append(p)

    faults_finder = earthquake_faults_finder.EarthquakeFaultsFinder()
    faults = faults_finder.find_candidate_faults(points)

    geojson_creation.object_list_to_geojson_file('faults', faults)

    riskfinder = risking_area_finder.RiskingAreaFinder()
    area = riskfinder.find_risking_area(faults)
    geojson_creation.object_list_to_geojson_file('area_at_risk', [area])
    geojson_creation.object_list_to_geojson_file('municipalities', area.get_municipalities())
