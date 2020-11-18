from queue import Queue
import tweepy


class Stream2Queue(tweepy.StreamListener):
    '''
    Stream listener used to store tweet coordinates in a queue
    '''

    def __init__(self, queue, api=None):
        '''

        @param queue: queue to store coords
        @param tweet_processor: object implementing tweetProcessorIF interface
        @param api: API to use
        '''
        self.api = api or tweepy.API()
        self.tweets = queue

    def on_status(self, status):
        '''
        called every time a tweet status is caught
        if the processor produces coords, they are stored in the queue
        @param status: tweepy status
        @return:
        '''
        self.tweets.put(status)


def __keys(name):
    '''
    @param name: API key (string)
    @return: API value (string)
    '''
    keychain = {'TwitKEY': 'nsq5BVLFe5xheMa9NO37poiob',
                'TwitSECRET': 'v2R6uHuzqkk68oM0P0KUAs0XkBezze3uBcujT2Dmlt6GclQJTh',
                'TwitTOKEN': '1270774916388917249-xDVbbwOTJk8kJyjG1SUs3l0NzSRYNg',
                'TwitTOKSEC': '24qRoFKDHiQb8D7tbhMdY56KBm8wYIWpDngBoLW0IgaqV'}
    return keychain[name]


def __get_API():
    auth = tweepy.OAuthHandler(__keys('TwitKEY'), __keys('TwitSECRET'))
    auth.set_access_token(__keys('TwitTOKEN'), __keys('TwitTOKSEC'))
    return tweepy.API(auth)


def put_tweets_in_queue_RT(queue: Queue, words_to_track=['a'], languages=['it'], user=None):

    api = __get_API()

    screen = Stream2Queue(queue)
    stream = tweepy.streaming.Stream(api.auth, screen)
    stream.filter(track=words_to_track, languages=languages, follow=user)
