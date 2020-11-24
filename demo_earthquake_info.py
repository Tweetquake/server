from server.earthquake_information import earthquake_faults_finder, risking_area_finder
from osgeo import osr, ogr

if __name__ == "__main__":
    from sklearn.datasets import make_blobs

    # generate samples (representing emergency tweets) within cities.
    # samples represent coordinates within Rome, Teramo, Pescara and  L'Aquila
    centers = [[13.33799, 42.29093],
               [12.51133, 41.89193], [13.69901, 42.66123], [14.20283, 42.4584]]
    X, labels_true = make_blobs(n_samples=20, centers=centers, cluster_std=0.5,
                                random_state=0)

    # actual test
    # We calculate clusters from points and export them as Polygons
    clusterizer = earthquake_faults_finder.PointClusterizer()
    clusters_as_polygons = clusterizer.get_concentrated_areas(X)

    # We find the earthquake affected area
    max_faults = 3  # maximum number of possible earthquake faults
    faults_finder = earthquake_faults_finder.earthquake_faults_finder(max_faults)
    faults = faults_finder.find_candidate_faults(clusters_as_polygons)

    for fault in faults:
        print(fault)

    riskfinder = risking_area_finder.risking_area_finder()
    area = riskfinder.find_risking_area(faults)

    print(area)