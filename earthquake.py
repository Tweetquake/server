from bottle import route, run, template, static_file

@route('/')
def start():
    return static_file('map.html', root="./client/")

@route('/client/map.js')
def start():
    return static_file('map.js', root="./client/")


run(host='localhost', port=8080, debug=True)