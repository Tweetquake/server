import os
import advertools as adv
import pandas as pd
from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from server.tweet_handling.tweet_filtering import FilteringMethod
from _pickle import load, dump


class EarthquakeTweetFM(FilteringMethod):
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
        self.classifier_path = 'server/tweet_handling/EarthquakeTweetFM' \
                               '/EarthquakeTweetFM_state/classifier.pkl '
        self.vectorizer_path = 'server/tweet_handling/EarthquakeTweetFM' \
                               '/EarthquakeTweetFM_state/vectorizer.pkl '
        if get_existing and \
                os.path.isfile(self.classifier_path) and \
                os.path.isfile(self.vectorizer_path):

            with open(self.classifier_path, 'rb') as fid:
                self.classifier = load(fid)

            with open(self.vectorizer_path, 'rb') as fid:
                self.vectorizer = load(fid)
        else:
            stop_words = sorted(adv.stopwords['italian'])
            stop_words.append('terremoto')
            self.classifier = svm.SVC(kernel='rbf', C=5.0, gamma='scale')
            self.vectorizer = TfidfVectorizer(min_df=0.00001,
                                              max_df=0.9,
                                              stop_words=stop_words,
                                              sublinear_tf=True,
                                              use_idf=True)

    def train(self, train_data: pd.DataFrame, save_to_file=False):
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

    def predict(self, data: pd.DataFrame):
        '''

        @param data: pandas csv with labels 'Content' (tweet text), 'Label'
        @return: array of labels
        '''
        test_vectors = self.vectorizer.transform(data['Content'])
        labels = self.classifier.predict(test_vectors)
        return labels


if __name__ == "__main__":
    '''
    execute this to train a new classifier
    '''
    data = pd.read_csv("server/tweet_handling/EarthquakeTweetFM/EarthquakeTweetFM_dataset.csv")

    train_data, test_data = train_test_split(data, test_size=0.1)

    detector = EarthquakeTweetFM(get_existing=False)
    detector.train(train_data=train_data, save_to_file=True)
    predictions = detector.predict(test_data)
    report = classification_report(test_data['Label'], predictions, output_dict=True)
    print('positive: ', report['pos'])
    print('negative: ', report['neg'])
    texts = ['ha fatto il terremoto', 'terremoto in politica',
             'Scossa: è crollato un ponte davanti ai miei occhi #terremoto']
    df = pd.DataFrame(texts, columns=['Content'])
    prediction = detector.predict(df)
    print()
    print(prediction)

    # print(detector.vectorizer.get_feature_names())
