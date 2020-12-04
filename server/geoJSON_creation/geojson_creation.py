from osgeo import ogr
from geojson import FeatureCollection, Feature, Point, Polygon

def object_list_to_geojson_file(filename, object_list):
    if object_list:
        file_path = 'server/geoJSON_creation/geojson_data/' + str(filename) + '.geojson'
        # Create the output Driver
        outDriver = ogr.GetDriverByName('GeoJSON')
        outDataSource = outDriver.CreateDataSource(file_path)
        outLayer = outDataSource.CreateLayer(file_path, geom_type=object_list[0].get_geometry().GetGeometryType())

        # Get the output Layer's Feature Definition
        featureDefn = outLayer.GetLayerDefn()

        # create fields
        for attribute in dir(object_list[0]):
            if attribute[0:3] == 'get' and attribute[4:len(attribute)] != 'geometry':  # take all the attributes (different from the geometry) by using the methods starting with "get"
                outLayer.CreateField(ogr.FieldDefn(attribute[4:len(attribute)], ogr.OFTString))

        for object in object_list:
            # create a new feature
            outFeature = ogr.Feature(featureDefn)

            # set geometry
            outFeature.SetGeometry(object.get_geometry())

            # set fields
            for attribute in dir(object):
                if attribute[0:3] == 'get' and attribute[4:len(attribute)] != 'geometry': #take all the attributes (different from the geometry) by using the methods starting with "get"
                    result = getattr(object, attribute)()
                    attr_value = ''
                    if type(result) == list:
                        attr_value = attr_value+'['
                        listToString = ', '.join([str(elem) for elem in result])
                        attr_value = attr_value+listToString+']'
                    else:
                        attr_value =str(result)
                    outFeature.SetField(attribute[4:len(attribute)], attr_value)
            outLayer.CreateFeature(outFeature)
        outFeature = None
        outDataSource = None
    else:
        print ('geojson file <'+filename+'> not created: there are no element in the list')

'''
def object_list_to_geojson(filename, object_list):
    features = []
    for object in object_list:
        geom = object.get_geometry()
        if (geom.GetGeometryType == 'POLYGON'):
        Feature(Polygon())
        print(wtk_geom)
        feature = Feature(POLYGON ((13.185225 42.519176,13.397271 42.378363,13.326091 42.319939,13.113885 42.460752,13.185225 42.519176)))
        feature = Feature(geometry = wtk_geom)
        features.append(feature)
    feature_collection = FeatureCollection(features)
    print(feature_collection)
'''