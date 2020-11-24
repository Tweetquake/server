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
        sleep(1)
        tweet_array = []
        while not tweets.empty():
            try:
                tweet_array.append(tweets.get())
            except queue.Empty:
                pass
        positives = tweet_filter.get_all_positives(tweet_array)
        for positive in positives:
            filtered_tweets.put(positive)

