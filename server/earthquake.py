from bottle import route, run, template

@route('/hello')
def hello():
    return "Hello World!"

@route('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)

@route('/')
def start():
    return '''
        <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no" />
    <title>Intro to MapView - Create a 2D map</title>
    <style>
        html,
        body,
        #viewDiv {
            padding: 0;
            margin: 0;
            height: 100%;
            width: 100%;
        }
    </style>
    <link rel="stylesheet" href="https://js.arcgis.com/4.17/esri/themes/light/main.css" />
    <script src="https://js.arcgis.com/4.17/"></script>
    <script src="../client/map.js"></script>
</head>
<body>
    <div id="viewDiv"></div>
</body>
</html>

    '''

run(host='localhost', port=8080, debug=True)