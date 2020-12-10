import threading
from queue import Queue

from bottle import route, run, template, static_file

from multithreading_processes import put_tweets_in_queue, filter_tweets_from_queue, \
    analyze_filtered_tweets


@route('/')
def get_map_html():
    return static_file('map.html', root="./client/")

@route('/map.js')
def get_map_js():
    return static_file('map.js', root="./client/")

@route('/area_at_risk.geojson')
def get_area_at_risk():
    return static_file('area_at_risk.geojson', root="./server/geoJSON_creation/geojson_data")

@route('/faults.geojson')
def get_faults():
    return static_file('faults.geojson', root="./server/geoJSON_creation/geojson_data")

@route('/municipalities.geojson')
def get_municipalities():
    return static_file('municipalities.geojson', root="./server/geoJSON_creation/geojson_data")

@route('/tweets.geojson')
def get_tweets():
    return static_file('tweets.geojson', root="./server/geoJSON_creation/geojson_data")





tweets = Queue()
filtered_tweets = Queue()

put_tweets_thread = threading.Thread(target=put_tweets_in_queue, args=(tweets,))
filter_tweets_thread = threading.Thread(target=filter_tweets_from_queue, args=(tweets, filtered_tweets,))
analyzer_thread = threading.Thread(target=analyze_filtered_tweets, args=(filtered_tweets,))

put_tweets_thread.start()
filter_tweets_thread.start()
analyzer_thread.start()

run(host='localhost', port=8080, debug=True)

put_tweets_thread.join()
filter_tweets_thread.join()
analyzer_thread.join()

