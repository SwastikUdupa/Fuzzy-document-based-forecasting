from fuzzification import Fuzzify
from score import TfIdf
from sort import Classify

import pandas as pd


def train():
    f = Fuzzify('data/sample.csv', 'output/sample.csv')
    f.run()
    c = Classify('output/sample.csv', 'output')
    c.run()
    test_f = Fuzzify('data/test.csv', 'output/test_sample.csv')
    test_f.run()


if __name__ == '__main__':

    train()
    df_test = pd.read_csv('output/test_sample.csv')
    tf_idf = TfIdf('output/bullish_sample.csv', 'output/neutral_sample.csv', 'output/bearish_sample.csv')

    correct = 0
    total = 0

    for x in range(4, len(df_test) - 10):
        total += 1
        md = df_test['md'][x]
        fcs = df_test['fcs'][x]
        max_score = 0
        max_score_doc = ''

        # Query these things against the database
        for y in ['bull', 'bear', 'neut']:
            md_ti = tf_idf.tfidf(md, y)
            fcs_ti = tf_idf.tfidf(fcs, y)
            score = md_ti + fcs_ti
            if score > max_score:
                max_score = score
                max_score_doc = y
        if max_score_doc == 'bull':
            max_score_doc = 'BL'
        elif max_score_doc == 'bear':
            max_score_doc = 'BR'
        else:
            max_score_doc = 'NT'

        actual = df_test['future'][x]
        if max_score_doc == actual:
            correct += 1

    print(correct/total)
