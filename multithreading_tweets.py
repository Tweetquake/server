import queue
from time import sleep
from server.tweet_handling.tweet_filtering import TweetFilter
from server.tweet_handling.tweet_retriever import put_tweets_in_queue_rt
from queue import Queue


# todo make a queue which has a semaphore that gets acquired if it is empty

def get_tweets_in_queue(tweets: Queue):
    put_tweets_in_queue_rt(tweets, words_to_track=['terremoto'])


def filter_tweets_from_queue(tweets: Queue, filtered_tweets: Queue):
    tweet_filter = TweetFilter()
    while True:
        tweet_array = []
        # blocks until the queue is not empty
        tweet_array.append(tweets.get())
        # checks if queue has more than 1 tweet
        while not tweets.empty():
            tweet_array.append(tweets.get())
        positives = tweet_filter.get_all_positives(tweet_array)
        for positive in positives:
            filtered_tweets.put(positive)
