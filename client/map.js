require(["esri/Map", "esri/views/MapView", "esri/widgets/BasemapToggle",
    "esri/layers/GeoJSONLayer", "esri/widgets/LayerList"],
    function(
    Map,
    MapView,
    BasemapToggle,
    GeoJSONLayer,
    LayerList
) {
    //Create templates for the layers
    //Area at risk template
    const template_ar = {
        title: "Area a rischio"
    };
    //Seismogenic sources template
    const template_ss = {
        title: "Faglie attive candidate",
        //content: "",
    };
    //Provincial capitals
    const template_pc = {
        title: "Capoluogo di provincia",
        content: "Comune di {comune}",
    };

    // Create GeoJSONLayer for the area at risk
    var geojsonLayer_area = new GeoJSONLayer({
        url: "areaAtRisk.geojson",
        popupTemplate: {
            title: "Area a rischio"
        }
    });

    // Create GeoJSONLayer for the seismogenic sources
    var geojsonLayer_sources = new GeoJSONLayer({
        url: "seismogenicSources.geojson",
        popupTemplate: template_ss
    });

    // Create GeoJSONLayer for the provincial capitals
    var geojsonLayer_capitals = new GeoJSONLayer({
        url: "provincial_capitals.geojson",
        popupTemplate: template_pc
    });

    // Create GeoJSONLayer for the seismogenic sources
    var geojsonLayer_road_nodes = new GeoJSONLayer({
        url: "road_nodes.geojson"
    });

    // Create GeoJSONLayer for the seismogenic sources
    var geojsonLayer_road_edges = new GeoJSONLayer({
        url: "road_edges.geojson"
    });

    // Create the Map with an initial basemap
    var map = new Map({
        basemap: "hybrid",
        layers: [geojsonLayer_area,geojsonLayer_sources,geojsonLayer_capitals,geojsonLayer_road_nodes,geojsonLayer_road_edges]
    });

    // Create the MapView and reference the Map in the instance
    var view = new MapView({
        container: "viewDiv",
        map: map,
        center: [12.492373, 41.890251],
        zoom: 6
    });

    // 1 - Create the widget
    var toggle = new BasemapToggle({
        // 2 - Set properties
        view: view, // view that provides access to the map's 'hybrid' basemap
        nextBasemap: "osm" // allows for toggling to the 'osm' basemap
    });

    // Add widget to the top right corner of the view
    view.ui.add(toggle, "top-right");

    view.when(function () {
        var layerList = new LayerList({
            view: view
        });

        // Add widget to the bottom right corner of the view
        view.ui.add(layerList, "bottom-right");
    });
    view.padding.left = 320;
});