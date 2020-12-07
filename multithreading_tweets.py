import threading
from time import sleep
from server.tweet_handling.tweet_filtering import TweetFilter, get_tweet_text
from server.tweet_handling.tweet_retriever import put_tweets_in_queue_rt
from queue import Queue



def put_tweets_in_queue(tweets: Queue):
    put_tweets_in_queue_rt(tweets, words_to_track=['terremoto'])


def filter_tweets_from_queue(tweets: Queue, filtered_tweets: Queue):
    tweet_filter = TweetFilter()
    while True:
        tweet_array = []
        # blocks until the queue is not empty
        tweet = tweets.get()
        # print is only for testing
        print(get_tweet_text(tweet))
        tweet_array.append(tweet)
        # checks if queue has more than 1 tweet
        while not tweets.empty():
            tweet = tweets.get()
            # print is only for testing
            print(get_tweet_text(tweet))
            tweet_array.append(tweet)
        positives = tweet_filter.get_all_positives(tweet_array)
        for positive in positives:
            filtered_tweets.put(positive)


def analyze_filtered_tweets(filtered_tweets: Queue):
    # TODO make the proper function
    while True:
        while not filtered_tweets.empty():
            print(filtered_tweets.get())


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