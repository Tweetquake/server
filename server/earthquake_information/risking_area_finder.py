from osgeo import osr, ogr


class RiskingAreaFinder:
    def __init__(self, faultsBuffer=0.3):
        self.faultsBuffer = faultsBuffer

    def find_risking_area(self, faults):
        union = ogr.Geometry(ogr.wkbPolygon)

        # find a 15km buffer for each candidate and do the union of them
        for fault in faults:
            union = union.Union(fault.Buffer(self.faultsBuffer))
        centroid = union.Centroid()

        return union

    def find_cities_at_risk(self):
        # Todo: searching cities at risk with cities500
        return 1

if __name__ == '__main__':
    '''
        example of finding risking area from faults polygons
    '''
    p1 = 'POLYGON ((13.51958 42.074493,13.759166 41.896436,13.692982 41.847152,13.453211 42.025209,13.51958 42.074493))'
    p2 = 'POLYGON ((13.937169 41.933693,14.079207 41.78818,14.00271 41.746726,13.860498 41.89224,13.937169 41.933693))'
    p3 = 'POLYGON ((13.185225 42.519176,13.397271 42.378363,13.326091 42.319939,13.113885 42.460752,13.185225 42.519176))'

    polygon1 = ogr.CreateGeometryFromWkt(p1)
    polygon2 = ogr.CreateGeometryFromWkt(p2)
    polygon3 = ogr.CreateGeometryFromWkt(p3)
    polygons = [polygon1, polygon2, polygon3]

    riskfinder = RiskingAreaFinder()
    area = riskfinder.find_risking_area(polygons)

    print(area)
