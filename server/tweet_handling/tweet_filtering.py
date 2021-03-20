from typing import List
import pandas as pd
from osgeo import ogr
from tweepy import Status


def get_tweet_text(tweet: Status):
    if hasattr(tweet, "retweeted_status"):  # Check if Retweet
        try:
            text = tweet.retweeted_status.extended_tweet["full_text"]
        except AttributeError:
            text = tweet.retweeted_status.text
    else:
        try:
            text = tweet.extended_tweet["full_text"]
        except AttributeError:
            text = tweet.text
    return text


def get_tweet_geom(tweet: Status):
    if tweet.place is not None:
        # we have to take the coords in the bounding_box
        box = tweet.place.bounding_box.coordinates
        # we take the first one in bbox, it could be improved in the future
        geom = box[0][0]
        x = geom[0]
        y = geom[1]
        geom = ogr.Geometry(ogr.wkbPoint)
        geom.AddPoint(x, y)
    else:
        geom = None

    return geom


def get_tweet_place(tweet: Status):
    place = tweet.place
    if place is None:
        place = None
    else:
        place = tweet.place.full_name
    return place


class TweetUsefulInfos(object):
    def __init__(self, tweet_status: Status):
        self.__text = get_tweet_text(tweet_status)
        self.__author = tweet_status.author.name
        self.__geometry = get_tweet_geom(tweet_status)
        self.__place = get_tweet_place(tweet_status)
        self.__time_posted = tweet_status.created_at

    def get_text(self):
        return self.__text

    def get_author(self):
        return self.__author

    def get_geometry(self):
        return self.__geometry

    def get_place(self):
        return self.__place

    def get_time_posted(self):
        return self.__time_posted

    def __str__(self):
        return 'Tweet text: {}\n posted at {}\n by {}\n the {}\n'.format(self.get_text(), self.get_place(),
                                                                         self.get_author(),
                                                                         self.get_time_posted())


class FilteringMethod:
    def __init__(self):
        pass

    def predict(self, data: pd.DataFrame):
        pass


class TweetFilter(object):
    def __init__(self, filtering_method: FilteringMethod):
        self.filtering_method = filtering_method

    def __get_by_label(self, tweets: List[TweetUsefulInfos], label: str):
        tweet_texts = []
        for tweet in tweets:
            tweet_texts.append(tweet.get_text())
        labels = self.filtering_method.predict(pd.DataFrame(tweet_texts, columns=['Content']))
        filtered_tweets = []
        for i in range(len(labels)):
            if labels[i] == label:
                filtered_tweets.append(tweets[i])
        return filtered_tweets

    def get_all_positives(self, tweets: List[TweetUsefulInfos]):
        positive_tweets = self.__get_by_label(tweets=tweets, label='pos')
        return positive_tweets

    def get_all_negatives(self, tweets: List[TweetUsefulInfos]):
        negative_tweets = self.__get_by_label(tweets=tweets, label='neg')
        return negative_tweets

