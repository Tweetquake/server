from queue import Queue

import tweepy

from server.tweet_handling.tweet_filtering import TweetUsefulInfos


class Stream2Queue(tweepy.StreamListener):
    '''
    Stream listener used to store tweet coordinates in a queue
    '''

    def __init__(self, queue: Queue, api=None):
        '''

        @param queue: queue to store coords
        @param api: API to use
        '''
        super().__init__(api)
        self.api = api or tweepy.API()
        self.tweets = queue

    def on_status(self, status):
        '''
        called every time a tweet status is caught
        if the processor produces coords, they are stored in the queue
        @param status: tweepy status
        @return:
        '''
        self.tweets.put(TweetUsefulInfos(status))
        print(status.text)


def __keys(name):
    '''
    @param name: API key (string)
    @return: API value (string)
    '''
    with open("keys.txt", "r") as f:
        keychain = {'TwitKEY': f.readline().strip(),
                    'TwitSECRET': f.readline().strip(),
                    'TwitTOKEN': f.readline().strip(),
                    'TwitTOKSEC': f.readline().strip()}
        return keychain[name]


def __get_API():
    auth = tweepy.OAuthHandler(__keys('TwitKEY'), __keys('TwitSECRET'))
    auth.set_access_token(__keys('TwitTOKEN'), __keys('TwitTOKSEC'))
    return tweepy.API(auth)


def put_tweets_in_queue_rt(queue: Queue, words_to_track=None, languages=None, user=None):
    if languages is None:
        languages = ['it']
    if words_to_track is None:
        words_to_track = ['a']
    api = __get_API()

    screen = Stream2Queue(queue)
    stream = tweepy.streaming.Stream(api.auth, screen)
    stream.filter(track=words_to_track, languages=languages, follow=user)
