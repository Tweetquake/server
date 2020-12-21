from osgeo import ogr

from server.earthquake_information import earthquake_faults_finder, risking_area_finder
from server.geoJSON_creation import geojson_creation

if __name__ == "__main__":
    '''
    example of finding earthquake faults from points
    '''

    p1 = ogr.Geometry(ogr.wkbPoint)
    p1.AddPoint(16.02055, 39.322077)
    p2 = ogr.Geometry(ogr.wkbPoint)
    p2.AddPoint(16.108425, 39.115321)
    p3 = ogr.Geometry(ogr.wkbPoint)
    p3.AddPoint(16.131526, 39.298742)
    p4 = ogr.Geometry(ogr.wkbPoint)
    p4.AddPoint(16.5434, 39.502651)
    p5 = ogr.Geometry(ogr.wkbPoint)
    p5.AddPoint(16.218534, 39.409581)
    p6 = ogr.Geometry(ogr.wkbPoint)
    p6.AddPoint(13.173664, 42.242641)

    points = [p1, p2, p3, p4, p5, p6]

    faults_finder = earthquake_faults_finder.EarthquakeFaultsFinder()
    faults = faults_finder.find_candidate_faults(points)

    geojson_creation.object_list_to_geojson_file('faults', faults)

    riskfinder = risking_area_finder.RiskingAreaFinder()
    area = riskfinder.find_risking_area(faults)
    geojson_creation.object_list_to_geojson_file('area_at_risk', [area])
    geojson_creation.object_list_to_geojson_file('municipalities', area.get_municipalities())
