from bottle import route, run, template, static_file

@route('/hello')
def hello():
    return "Hello World!"

@route('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)

@route('/')
def start():
    return static_file('map.html' , root="../client/")

@route('/client/map.js')
def start():
    return static_file('map.js', root="../client/")


run(host='localhost', port=8080, debug=True)