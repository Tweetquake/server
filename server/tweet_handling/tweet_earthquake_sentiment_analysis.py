import _pickle as cPickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import os.path

from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


class tweet_earthquake_SA(object):
    '''
    used to check if a tweet talks about an earthquake happening now or not
    using sentiment analysis
    '''

    def __init__(self, get_existing=True):
        '''
        checks if a SVM and a corresponding vectorizer exists.
        if so it loads their states
        otherwise it initializes two new one
        '''
        self.classifier_path = 'tweet_earthquake_sentiment_analisys_data/SVM_state/classifier.pkl'
        self.vectorizer_path = 'tweet_earthquake_sentiment_analisys_data/SVM_state/vectorizer.pkl'
        if get_existing and \
                os.path.isfile(self.classifier_path) and \
                os.path.isfile(self.vectorizer_path):

            with open(self.classifier_path, 'rb') as fid:
                self.classifier = cPickle.load(fid)

            with open(self.vectorizer_path, 'rb') as fid:
                self.vectorizer = cPickle.load(fid)
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
                cPickle.dump(self.classifier, fid)
            with open(self.vectorizer_path, 'wb') as fid:
                cPickle.dump(self.vectorizer, fid)

    def predict(self, data: pd.DataFrame):
        '''

        @param data: pandas csv with labels 'Content' (tweet), 'Label'
        @return: array of labels
        '''
        test_vectors = self.vectorizer.transform(data)
        labels = self.classifier.predict(test_vectors)
        return labels


if __name__ == "__main__":
    '''
    execute this to train a new classifier
    '''
    data = pd.read_csv(
        "tweet_earthquake_sentiment_analisys_data/earthquake_sentiment_analysis_dataset/earthquake_dataset_SA.csv")

    train_data, test_data = train_test_split(data, test_size=0.9)

    detector = tweet_earthquake_SA()
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
