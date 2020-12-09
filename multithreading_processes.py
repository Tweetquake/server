import threading
from datetime import datetime, timedelta
from time import sleep

from typing import List

from tweepy import Status

from server.earthquake_information import earthquake_faults_finder, risking_area_finder
from server.geoJSON_creation import geojson_creation
from server.tweet_handling.tweet_filtering import TweetFilter, get_tweet_text, TweetUsefulInfos
from server.tweet_handling.tweet_retriever import put_tweets_in_queue_rt
from queue import Queue

class EarthquakeDetection:
    def __init__(self, number_of_earthquakes: int, time_window: timedelta):
        self.earthquakes = number_of_earthquakes
        self.time_window = time_window
        self.tweets_in_time_window = []
        self.last_tweet_time_added = None

    def put_tweets_datetimes(self, tweets_datetimes: List[datetime]):
        self.last_tweet_time_added = tweets_datetimes[-1]
        self.tweets_in_time_window += tweets_datetimes

    def is_detected(self):
        # removes elements not in timewindow
        while self.last_tweet_time_added - self.time_window > self.tweets_in_time_window[0]:
            self.tweets_in_time_window.pop(0)

        # checks if elements in timewindow are enough to say that an earthquake is detected
        if len(self.tweets_in_time_window) >= self.earthquakes:
            is_detected = True
        else:
            is_detected = False
        return is_detected

    def get_time_window_end(self):
        return datetime.now()-self.time_window



def put_tweets_in_queue(tweets: Queue):
    put_tweets_in_queue_rt(tweets, words_to_track=['terremoto'])


def filter_tweets_from_queue(tweets: Queue, filtered_tweets: Queue):
    tweet_filter = TweetFilter()
    while True:
        tweet_array = []
        # blocks until the queue is not empty
        tweet = tweets.get()
        tweet_array.append(tweet)
        # checks if queue has more than 1 tweet
        while not tweets.empty():
            tweet = tweets.get()
            # print is only for testing
            tweet_array.append(tweet)
        positives = tweet_filter.get_all_positives(tweet_array)
        for positive in positives:
            useful_infos_tweet = TweetUsefulInfos(positive)
            filtered_tweets.put(useful_infos_tweet)

# TODO finish this function
def analyze_filtered_tweets(filtered_tweets: Queue):
    # we detect an earthquake if 5 tweets are posted in the last 5 minutes
    detection = EarthquakeDetection(number_of_earthquakes=5, time_window=timedelta(seconds=5*60))
    tweets_2_analyze = []
    tweets_2_analyze_datetimes = []
    while True:
        # this is made in order to block this thread
        filtered_tweet = filtered_tweets.get()
        tweets_2_analyze.append(filtered_tweet)
        tweets_2_analyze_datetimes.append(filtered_tweet.get_time_posted())
        while not filtered_tweets.empty():
            filtered_tweet = filtered_tweets.get()
            tweets_2_analyze.append(filtered_tweet)
            tweets_2_analyze_datetimes.append(filtered_tweet.get_time_posted())
        if tweets_2_analyze_datetimes:
            detection.put_tweets_datetimes(tweets_datetimes=tweets_2_analyze_datetimes)
        while detection.is_detected():
            print("detected")
            # this is made in order to block this thread
            filtered_tweet = filtered_tweets.get()
            tweets_2_analyze.append(filtered_tweet)
            tweets_2_analyze_datetimes.append(filtered_tweet.get_time_posted())
            while not filtered_tweets.empty():
                filtered_tweet = filtered_tweets.get()
                tweets_2_analyze.append(filtered_tweet)
                tweets_2_analyze_datetimes.append(filtered_tweet.get_time_posted())
            if tweets_2_analyze_datetimes:
                detection.put_tweets_datetimes(tweets_datetimes=tweets_2_analyze_datetimes)
        print("not detected")

def create_geojsons(tweet_list):
    geojson_creation.object_list_to_geojson_file('tweets', tweet_list)
    faults_finder = earthquake_faults_finder.EarthquakeFaultsFinder()
    gdal_points = []
    for tweet in tweet_list:
        gdal_points.append(tweet.get_geometry())
    faults = faults_finder.find_candidate_faults(gdal_points)
    geojson_creation.object_list_to_geojson_file('faults', faults)

    riskfinder = risking_area_finder.RiskingAreaFinder()
    area = riskfinder.find_risking_area(faults)
    geojson_creation.object_list_to_geojson_file('area_at_risk', [area])
    geojson_creation.object_list_to_geojson_file('municipalities', area.get_municipalities())

if __name__ == "__main__":
    tweets = Queue()
    filtered_tweets = Queue()

    put_tweets_thread = threading.Thread(target=put_tweets_in_queue, args=(tweets,))
    filter_tweets_thread = threading.Thread(target=filter_tweets_from_queue, args=(tweets, filtered_tweets,))
    analyzer_thread = threading.Thread(target=analyze_filtered_tweets, args=(filtered_tweets,))

    put_tweets_thread.start()
    filter_tweets_thread.start()
    analyzer_thread.start()

    put_tweets_thread.join()
    filter_tweets_thread.join()
    analyzer_thread.join()

    print("code should never get here")