require(["esri/Map", "esri/views/MapView", "esri/widgets/BasemapToggle",
    "esri/layers/GeoJSONLayer", "esri/widgets/LayerList"],
    function(
    Map,
    MapView,
    BasemapToggle,
    GeoJSONLayer,
    LayerList
    ) {
        // Create templates for the layers
        // Tweets template
        const template_tweets = {
                title: "Tweet di {author} da {place}, {time_posted}",
                content: "'{text}'",
                fieldInfos: [
                    {
                        fieldName: "time_posted",
                        format: {
                            dateFormat: "long-month-day-year-short-time-24"
                        }
                    }]
        };
        // Area at risk template
        const template_risking_area = {
            title: "Area a rischio",
            content: "Popolazione totale: {population}"
        };
        // Seismogenic faults template
        const template_faults = {
            title: "Faglie attive candidate",
            content: "Probabilità: {probability}",
        };
        // Municipalities at risk template
        const template_municipalities = {
            title: "{name} ({province})",
            content: "Numero di abitanti: {population}"
        };
    
        // Create renderers for the layers
        // Tweets renderer
        const renderer_tweets = {
            type: "simple",
            symbol: {
                type: "simple-marker",
                size: 6,
                color: "#0ED2F9",
                outline: {
                    width: 0.5,
                    color: "white"
                }
            }
        }
        // Faults renderer
        const renderer_faults = {
            type: "simple",
            symbol: {
                type: "simple-fill",
                color: "black",
                outline: {
                    width: 0.5,
                    color: "white"
                }
            }
        }
        // Risking Area renderer
        const renderer_risking_area = {
            type: "simple",
            symbol: {
                type: "simple-fill",
                color: "#ff8080",
                opacityValue: 0.5,
                outline: {
                    width: 0.5,
                    color: "white"
                }
            }
        }
        // Municipalities renderer
        const renderer_municipalities = {
            type: "simple",
            symbol: {
                type: "simple-marker",
                color: "#cc0000",
                outline: {color: "white"}
            },
            visualVariables: [{
                    type: "size",
                    field: "population",
                    stops: [
                        {value: 100, size: "4px"},
                        {value: 40000, size: "20px"}
                    ]
            }]
        };

        // Create GeoJSON layers
        // Create GeoJSONLayer for tweets
        var geojsonLayer_tweets = new GeoJSONLayer({
            url: "tweets.geojson",
            title: 'Tweet',
            popupTemplate: template_tweets,
            renderer: renderer_tweets
        });

        // Create GeoJSONLayer for seismogenic faults
        var geojsonLayer_faults = new GeoJSONLayer({
            url: "faults.geojson",
            title: 'Probabili faglie attivate',
            popupTemplate: template_faults,
            renderer: renderer_faults,
            opacity: 0.5
        });

        // Create GeoJSONLayer for area at risk
        var geojsonLayer_risking_area = new GeoJSONLayer({
            url: "area_at_risk.geojson",
            title: 'Area a rischio',
            popupTemplate: template_risking_area,
            renderer: renderer_risking_area,
            blendMode: "multiply",
            opacity: 0.9
        });

        // Create GeoJSONLayer for municipalities at risk
        var geojsonLayer_municipalities = new GeoJSONLayer({
            url: "municipalities.geojson",
            title: 'Zone a rischio',
            popupTemplate: template_municipalities,
            renderer: renderer_municipalities
        });

        // Create the Map with an initial basemap
        var map = new Map({
            basemap: "hybrid",
            //layers: [geojsonLayer_faults,geojsonLayer_risking_area,geojsonLayer_municipalities,geojsonLayer_tweets]
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
    
        var layerList = new LayerList({
            view: view,
        });

        map.add(geojsonLayer_risking_area);
        map.add(geojsonLayer_faults);
        map.add(geojsonLayer_municipalities);
        map.add(geojsonLayer_tweets);
    
        // Add widget to the top right corner of the view
        view.ui.add(toggle, "top-right");
    
        // Add widget to the bottom right corner of the view
        view.ui.add(layerList, "bottom-right");
    
        view.padding.left = 320;

        setInterval(function(){
            //qua ci andrebbe l'aggiornamento del layer
            }, 5000); //refresh every 5 sec
        }

);


