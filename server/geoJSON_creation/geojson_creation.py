from osgeo import ogr


def object_list_to_geojson_file(filename, object_list):
    if object_list:
        file_path = 'server/geoJSON_creation/geojson_data/' + str(filename) + '.geojson'
        # Create the output Driver
        outDriver = ogr.GetDriverByName('GeoJSON')
        outDataSource = outDriver.CreateDataSource(file_path)
        outLayer = outDataSource.CreateLayer(filename.replace("_", " ").title(),
                                             geom_type=object_list[0].get_geometry().GetGeometryType())

        # Get the output Layer's Feature Definition
        featureDefn = outLayer.GetLayerDefn()

        # create fields
        for attribute in dir(object_list[0]):
            if attribute[0:3] == 'get' and attribute[4:len(
                    attribute)] != 'geometry':  # take all the attributes (different from the geometry) by using the methods starting with "get"
                outLayer.CreateField(ogr.FieldDefn(attribute[4:len(attribute)], ogr.OFTString))

        for object in object_list:
            if object.get_geometry:
                # create a new feature
                outFeature = ogr.Feature(featureDefn)

                # set geometry
                outFeature.SetGeometry(object.get_geometry())

                # set fields
                for attribute in dir(object):
                    if attribute[0:3] == 'get' and attribute[4:len(
                            attribute)] != 'geometry':  # take all the attributes (different from the geometry) by using the methods starting with "get"
                        result = getattr(object, attribute)()
                        attr_value = ''
                        if type(result) == list:
                            attr_value = attr_value + '['
                            list_to_string = ', '.join([str(elem) for elem in result])
                            attr_value = attr_value + list_to_string + ']'
                        else:
                            attr_value = str(result)
                        outFeature.SetField(attribute[4:len(attribute)], attr_value)
                outLayer.CreateFeature(outFeature)
        outFeature = None
        outDataSource = None
    else:
        print('geojson file <' + filename + '> not created: there are no element in the list')
