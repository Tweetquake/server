from _pickle import load, dump
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import os.path

from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
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
    if tweet.coordinates is not None:
        geom = tweet.coordinates
    elif tweet.place is not None:
        # we have to take the coords in the bounding_box
        box = tweet.place.bounding_box.coordinates
        # we take the first one in bbox, it could be improved in the future
        geom = box[0][0]
    else:
        geom = None
    return geom


class TweetUsefulInfos(object):
    def __init__(self, tweet_status: Status):
        self.__text = get_tweet_text(tweet_status)
        self.__author = tweet_status.author.name
        self.__geometry = get_tweet_geom(tweet_status)
        self.__place = tweet_status.place
        self.__time_posted = tweet_status.created_at

    def get_text(self):
        return self.__text

    def get_author(self):
        return self.__author

    def get_coordinates(self):
        return self.__coordinates

    def get_place(self):
        return self.__place

    def time_posted(self):
        return self.__time_posted


class TweetFilter(object):
    def __init__(self):
        self.sentiment_analysis = TweetEarthquakeSA()

    def __get_by_label(self, tweets: [], label: str):
        tweet_texts = []
        for tweet in tweets:
            tweet_texts.append(get_tweet_text(tweet))
        labels = self.sentiment_analysis.predict(tweet_texts)
        filtered_tweets = []
        for i in range(len(labels)):
            if labels[i] is label:
                filtered_tweets.append(tweets[i])
        return filtered_tweets

    def get_all_positives(self, tweets: []):
        positive_tweets = self.__get_by_label(tweets=tweets, label='pos')
        return positive_tweets

    def get_all_negatives(self, tweets: []):
        negative_tweets = self.__get_by_label(tweets=tweets, label='neg')
        return negative_tweets


class TweetEarthquakeSA(object):
    """
    used to check if a tweet talks about an earthquake happening now or not
    using sentiment analysis
    """

    def __init__(self, get_existing=True):
        """
        checks if a SVM and a corresponding vectorizer exists.
        if so it loads their states
        otherwise it initializes two new one
        """
        self.classifier_path = 'tweet_earthquake_sentiment_analysis_data/SVM_state/classifier.pkl'
        self.vectorizer_path = 'tweet_earthquake_sentiment_analysis_data/SVM_state/vectorizer.pkl'
        if get_existing and \
                os.path.isfile(self.classifier_path) and \
                os.path.isfile(self.vectorizer_path):

            with open(self.classifier_path, 'rb') as fid:
                self.classifier = load(fid)

            with open(self.vectorizer_path, 'rb') as fid:
                self.vectorizer = load(fid)
        else:
            self.classifier = svm.SVC(kernel='linear', C=3.3, gamma='auto')
            self.vectorizer = TfidfVectorizer(min_df=5,
                                              max_df=0.8,
                                              sublinear_tf=True,
                                              use_idf=True)

    def train(self, train_data, save_to_file=False):
        '''
        @param train_data: pandas csv with labels 'Content' (tweet), 'Label'
        @param save_to_file: bool
        @return:
        '''
        train_vectors = self.vectorizer.fit_transform(train_data['Content'])
        self.classifier.fit(train_vectors, train_data['Label'])
        if save_to_file:
            with open(self.classifier_path, 'wb') as fid:
                dump(self.classifier, fid)
            with open(self.vectorizer_path, 'wb') as fid:
                dump(self.vectorizer, fid)

    def predict(self, data: []):
        '''

        @param data: pandas csv with labels 'Content' (tweet), 'Label'
        @return: array of labels
        '''
        data = pd.DataFrame(data, columns=['Content'])
        test_vectors = self.vectorizer.transform(data)
        labels = self.classifier.predict(test_vectors)
        return labels


if __name__ == "__main__":
    '''
    execute this to train a new classifier
    '''
    data = pd.read_csv(
        "tweet_earthquake_sentiment_analysis_data/earthquake_sentiment_analysis_dataset/earthquake_dataset_SA.csv")

    train_data, test_data = train_test_split(data, test_size=0.9)

    detector = TweetEarthquakeSA()
    detector.train(train_data=train_data, save_to_file=True)
    predictions = detector.predict(test_data['Content'])
    report = classification_report(test_data['Label'], predictions, output_dict=True)
    print('positive: ', report['pos'])
    print('negative: ', report['neg'])
    texts = ['ha fatto il terremoto', 'terremoto in politica',
             'Scossa: è crollato un ponte davanti casa mia #terremoto']
    df = pd.DataFrame(texts, columns=['Content'])
    prediction = detector.predict(df['Content'])
    print()
    print(prediction)