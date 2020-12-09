from typing import List

import numpy as np
from scipy.spatial.qhull import ConvexHull
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from osgeo import ogr


class PointsToPolygon:
    def __init__(self):
        pass

    def get_concentrated_areas(self, point_list):
        pass


class PointClusterizer(PointsToPolygon):
    """
    This class calculates clusters from a list of geographic
    points splitting them into lists. For each cluster, non meaningful
    points are removed as well as noise.
    It also calculates a convex hull for each cluster.
    """

    def __init__(self, eps=0.5, min_samples=5):

        self.__eps = eps
        self.__min_samples = min_samples

        self.__total_clusters = 0
        self.__cluster_points = None
        self.__cluster_hulls = None

    def __calculate_clusters(self, point_list):
        """
        calculates and saves clusters using DBSCAN
        """
        scaler = StandardScaler()
        X = scaler.fit_transform(point_list)
        db = DBSCAN(eps=self.__eps, min_samples=self.__min_samples).fit(X)
        X = scaler.inverse_transform(X)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        cluster_points = []
        for k in range(n_clusters_):
            class_member_mask = (labels == k)
            points_in_cluster_k = X[class_member_mask & core_samples_mask]
            cluster_points.append(points_in_cluster_k.tolist())
        self.__cluster_points = cluster_points
        self.__total_clusters = n_clusters_

    def __clusters2hulls(self):
        """
        calculates a convex hull for each cluster.
        @return:
        """
        hulls = []
        n_clusters = self.__total_clusters
        cluster_points = self.__cluster_points
        for i in range(n_clusters):
            if len(cluster_points[i]) > 2:
                hull = ConvexHull(cluster_points[i])
            else:
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(cluster_points[i][0][0], cluster_points[i][0][1])
                buffer = point.Buffer(0.01)
                boundary = buffer.Boundary()
                bufPoints = []
                for i in range(boundary.GetPointCount()):
                    x, y, not_needed = boundary.GetPoint(i)
                    bufPoints.append([x, y])
                hull = ConvexHull(bufPoints)
            '''else:
                self.total_clusters = self.total_clusters-1'''
            hulls.append(hull)
        self.__cluster_hulls = hulls

    def __get_cluster_hulls_as_gdal_poly(self):
        """

        @return: an array containing a GDAL polygon for each cluster
        """
        gdhulls = []
        for i in range(self.__total_clusters):
            hull = self.__cluster_hulls[i]
            points_in_cluster = hull.points
            ring = ogr.Geometry(ogr.wkbLinearRing)

            # get x and y coordinates (x and y are np.array)
            x = points_in_cluster[hull.vertices, 0]
            y = points_in_cluster[hull.vertices, 1]

            # get points
            for i in range(len(x)):
                ring.AddPoint(x[i], y[i])
            # close the polygon
            ring.AddPoint(x[0], y[0])

            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)
            gdhulls.append(poly)
        return gdhulls

    def __gdal_2_np(self, points_list):
        list = []
        for point in points_list:
            x = point.GetX()
            y = point.GetY()
            list.append([x,y])
        np_list = np.array(list)
        return np_list

    def get_eps(self):
        return self.__eps

    def get_min_samples(self):
        return self.__min_samples

    def set_eps(self, eps: float):
        self.__eps = eps

    def set_min_samples(self, min_samples: int):
        self.__min_samples = min_samples

    def get_concentrated_areas(self, point_list):
        point_list = self.__gdal_2_np(point_list)
        self.__calculate_clusters(point_list)
        self.__clusters2hulls()
        return self.__get_cluster_hulls_as_gdal_poly()


class EarthquakeFaultsFinder:
    """
       This class finds the possible earthquake faults from a list
       of GDAL polygons which represent the clusters of the sensors.
       It is possible to set a maximum number of possible faults.
       """

    def __init__(self, max_faults=3, polygons_buffer=0.7, points2polygon: PointsToPolygon = PointClusterizer()):
        self.__maximum_number_of_faults = max_faults
        self.__polygons_buffer = polygons_buffer
        self.__possible_faults = []
        self.__points2polygon = points2polygon


    def get_maximum_number_of_faults(self):
        return self.__maximum_number_of_faults

    def get_polygons_buffer(self):
        return self.__polygons_buffer

    def set_maximum_number_of_faults(self, max_faults: int):
        if max_faults > 0:
            self.__maximum_number_of_faults = max_faults

    def set_polygons_buffer(self, polygons_buffer: float):
        if polygons_buffer > 0:
            self.__polygons_buffer = polygons_buffer

    def find_candidate_faults(self, point_list):
        polygons = self.__points2polygon.get_concentrated_areas(point_list)
        candidates_count, candidates = self.__find_all_candidate_faults(polygons)
        for i in range(0, len(candidates_count)):
            fault = EarthquakeFault(candidates[i], candidates_count[i][1])
            self.add_faults(fault)
        if self.__maximum_number_of_faults == 0:
            faults = self.__possible_faults
        else:
            faults = []
            for i in range(0, min(self.__maximum_number_of_faults, len(candidates_count))):
                faults.append(self.__possible_faults[i])
        return faults

    def __find_all_candidate_faults(self, polygons):
        # load the composite seismologic sources from the shapefile 'CSSPLN321.shp''
        driver = ogr.GetDriverByName("ESRI Shapefile")
        file_seism = 'server/earthquake_information/INGV/ISS321.shp'
        vector_seism = driver.Open(file_seism, 0)
        layer_seism = vector_seism.GetLayer(0)

        # Find nearest seismologic sources for each area (e.g. with dist of 20 km)
        candidates_count = {}
        candidates = []
        for polygon in polygons:
            sources = self.__find_nearest_faults(polygon, layer_seism)
            for source in sources:
                sourceID = source.GetField(0)
                if sourceID in candidates_count:
                    candidates_count[sourceID] = candidates_count[sourceID] + 1
                else:
                    candidates_count[sourceID] = 1
                    source_geom = source.GetGeometryRef().GetGeometryRef(0)
                    source_poly = ogr.Geometry(ogr.wkbPolygon)
                    source_poly.AddGeometry(source_geom)
                    candidates.append(source_poly)

        sorted_candidates_count = sorted(candidates_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates_count, candidates

    def __find_nearest_faults(self, polygon, layer_seism):

        area = polygon.Buffer(self.__polygons_buffer)

        faults = []
        for fault in layer_seism:
            fault_geom = fault.GetGeometryRef().GetGeometryRef(0)
            fault_poly = ogr.Geometry(ogr.wkbPolygon)
            fault_poly.AddGeometry(fault_geom)

            if area.Intersects(fault_poly):
                faults.append(fault)

        return faults

    def add_faults(self, fault):
        self.__possible_faults.append(fault)


class EarthquakeFault(object):
    '''
    This class define a possible earthquake faults.
    Since it is not possible to know for sure which fault
    generated the earthquake, every possible faults have a probability.
    '''

    def __init__(self, gdal_geometry, probability):
        self.__geometry = gdal_geometry
        self.__probability = probability

    def set_probability(self, prob):
        if prob > 0:
            self.__probability = prob

    def get_geometry(self):
        return self.__geometry

    def get_probability(self):
        return self.__probability


if __name__ == '__main__':
    '''
        example of finding earthquake faults from polygons
    '''
    p1 = 'POLYGON((13.5068345450051 42.453405113893 0, 13.4096230499813 42.4523491454874 0, 13.2115443247965 42.4064643249082 0, 13.1851261157124 42.3844347578868 0, 13.1862671506709 42.337148180385 0, 13.2258412924453 42.2526387443975 0, 13.2423197602569 42.2312002178368 0, 13.3705863707811 42.1833929419606 0, 13.4698105487939 42.19658686572 0, 13.5302690593105 42.2821405484086 0, 13.5230236642177 42.3785610045857 0, 13.5068345450051 42.453405113893 0))'
    p2 = 'POLYGON((14.2465962015719 42.3462559641075 0, 14.2859920854647 42.4805859828347 0, 14.256855338585 42.5160452907775 0, 14.1304330010751 42.5061116162797 0, 14.1123300163194 42.4770935608544 0, 14.1465913235078 42.4101315155575 0, 14.1780504262123 42.3621534094607 0, 14.2465962015719 42.3462559641075 0))'
    p3 = 'POLYGON((12.422396050106 41.9597877695711 0, 12.4823766713468 41.8396081631992 0, 12.5776376377442 41.8810792934836 0, 12.6420591272299 41.9553531260793 0, 12.6459359418536 41.9955660354004 0, 12.4808692513795 42.0213784609936 0, 12.4510442020462 42.0256345467169 0, 12.429211361642 42.0279834829955 0, 12.422396050106 41.9597877695711 0))'
    p4 = 'POLYGON((13.6289949256827 42.5530960232256 0, 13.7778745145475 42.5856347944146 0, 13.7654694564848 42.667358586897 0, 13.6942330876273 42.7811639905155 0, 13.6351124442189 42.7394211401667 0, 13.6132295136819 42.7203354083481 0, 13.5946219685106 42.6919874190885 0, 13.6068964812642 42.628919077663 0, 13.6289949256827 42.5530960232256 0))'

    polygon1 = ogr.CreateGeometryFromWkt(p1)
    polygon2 = ogr.CreateGeometryFromWkt(p2)
    polygon3 = ogr.CreateGeometryFromWkt(p3)
    polygon4 = ogr.CreateGeometryFromWkt(p4)
    polygons = [polygon1, polygon2, polygon3, polygon4]

    max_faults = 3  # maximum number of possible earthquake faults

    faultsfinder = EarthquakeFaultsFinder(max_faults)
    faults = faultsfinder.find_candidate_faults(points)

    for fault in faults:
        print(fault.get_geometry())
