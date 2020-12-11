import numpy as np
from osgeo import ogr
from scipy.spatial.qhull import ConvexHull
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


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
            list.append([x, y])
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

    def add_faults(self, fault):
        self.__possible_faults.append(fault)

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
        # load the composite seismologic sources from the shapefile 'ISS321.shp''
        driver = ogr.GetDriverByName("ESRI Shapefile")
        file_seism = 'server/earthquake_information/INGV/ISS321.shp'
        vector_seism = driver.Open(file_seism, 0)
        layer_seism = vector_seism.GetLayer(0)
        # Find probability of seismogenic faults for each polygons (e.g. with dist of 20 km)
        polygons_probabilities = {}
        for polygon in polygons:
            distances = {} #dictionary fault -> distance from this polygon
            faults_probabilities = {}
            sum = 0
            for fault in layer_seism:
                fault_geom = fault.GetGeometryRef().GetGeometryRef(0)
                fault_poly = ogr.Geometry(ogr.wkbPolygon)
                fault_poly.AddGeometry(fault_geom)
                distance = 1/(polygon.Distance(fault_poly))
                distances[fault.GetField(0)] = distance
                sum = sum + distance
            for fault in layer_seism:
                faults_probabilities[fault.GetField(0)] = distances[fault.GetField(0)]/sum
            polygons_probabilities[polygon] = faults_probabilities
        probabilities_sum = {}
        faults = []
        for fault in layer_seism:
            fault_geom = fault.GetGeometryRef().GetGeometryRef(0)
            fault_poly = ogr.Geometry(ogr.wkbPolygon)
            fault_poly.AddGeometry(fault_geom)
            prob_fault = 0
            for polygon in polygons:
                prob_fault = prob_fault + polygons_probabilities[polygon][fault.GetField(0)]
            prob_fault = prob_fault/len(polygons)
            probabilities_sum[fault.GetField(0)] = prob_fault
            faults.append(fault_poly)

        sorted_candidates_count = sorted(probabilities_sum.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates_count, faults

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

    def __find_distances_from_faults(self, polygon, layer_seism):
        faults_distances = {}
        for fault in layer_seism:
            fault_geom = fault.GetGeometryRef().GetGeometryRef(0)
            fault_poly = ogr.Geometry(ogr.wkbPolygon)
            fault_poly.AddGeometry(fault_geom)
            faults_distances[fault] = polygon.Distance(fault_poly)
        return faults_distances


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

    faults_finder = EarthquakeFaultsFinder()
    faults = faults_finder.find_candidate_faults(points)

    for fault in faults:
        print(fault.get_geometry(), fault.get_probability())
