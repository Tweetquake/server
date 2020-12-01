from osgeo import osr, ogr


class RiskingAreaFinder:
    def __init__(self, faultsBuffer=0.3):
        self.faultsBuffer = faultsBuffer

    # todo use class EarthquakeFaults
    def find_risking_area(self, faults: []):
        risking_area_geom = ogr.Geometry(ogr.wkbPolygon)

        # find a 15km buffer for each candidate and do the union of them
        for fault in faults:
            risking_area_geom = risking_area_geom.Union(fault.get_geometry().Buffer(self.faultsBuffer))
        centroid = risking_area_geom.Centroid()

        municipalities, population = self.__find_cities_at_risk(risking_area_geom)
        return RiskingArea(risking_area_geom, municipalities, population)

    @staticmethod
    def __find_cities_at_risk(area):
        drvName = "ESRI Shapefile"
        driver = ogr.GetDriverByName(drvName)
        italy_shp = 'server/earthquake_information/cities500/cities500_IT.shp'
        vector_italy = driver.Open(italy_shp, 0)
        layer_italy = vector_italy.GetLayer(0)
        earthquake_municipalities = []

        srs_italy = layer_italy.GetSpatialRef()
        target_osr = osr.SpatialReference()
        target_osr.ImportFromEPSG(32632)  # SRS of UTM 32N
        transform = osr.CoordinateTransformation(srs_italy, target_osr)

        earthquake_population = 0
        for feature in layer_italy:
            geom = feature.GetGeometryRef()
            geom.Transform(transform)
            if geom.Within(area):
                name_id = feature.GetFieldIndex("name")
                population_id = feature.GetFieldIndex("population")
                country_code_id = feature.GetFieldIndex("country code")
                province_id = feature.GetFieldIndex("province")
                name = feature.GetField(name_id)
                population = feature.GetField(population_id)
                country = feature.GetField(country_code_id)
                province = feature.GetField(province_id)
                earthquake_municipalities.append(Municipality(name, province, country,
                                                              population, geom))
                earthquake_population += int(population)

        return earthquake_municipalities, earthquake_population


class RiskingArea(object):
    def __init__(self, geometry, municipalities: [], population: int):
        self.__geometry = geometry
        self.__municipalities = municipalities
        self.__population = population

    def get_geometry(self):
        return self.__geometry

    def get_municipalities(self):
        return self.__municipalities

    def get_population(self):
        return self.__population

    def get_centroid(self):
        return self.__geometry.Centroid()


class Municipality(object):
    def __init__(self, name, province, state, population, geometry):
        self.__name = name
        self.__province = province
        self.__state = state
        self.__population = population
        self.__geometry = geometry

    def get_name(self):
        return self.__name

    def get_province(self):
        return self.__province

    def get_state(self):
        return self.__state

    def get_populatuion(self):
        return self.__population

    def get_geometry(self):
        return self.__geometry

    def get_centroid(self):
        return self.__geometry.Centroid()


if __name__ == '__main__':
    from server.earthquake_information.earthquake_faults_finder import EarthquakeFault

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

    fault1 = EarthquakeFault(polygon1, 0.4)
    fault2 = EarthquakeFault(polygon2, 0.6)
    fault3 = EarthquakeFault(polygon3, 0.3)

    faults = [fault1, fault2, fault3]
    riskfinder = RiskingAreaFinder()
    area = riskfinder.find_risking_area(faults)

    print(area.get_population())
