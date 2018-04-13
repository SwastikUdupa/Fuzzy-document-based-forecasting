import pandas as pd
import numpy as np
import math


class TfIdf(object):

    def __init__(self, fbull, fneut, fbear, term1, term2):
        self.bullish = fbull
        self.neutral = fneut
        self.bearish = fbear
        self.term1 = term1
        self.term2 = term2
        self.docs = 3

    def get_file(self, cat):
        # TODO: Write documentation
        if 'bull' in cat.lower():
            return self.bullish
        elif 'bear' in cat.lower():
            return self.bearish
        else:
            return self.neutral

    def _read_csv(self, csv_file):
        df = pd.read_csv(csv_file)
        return df

    def _read_text(self, csv_file):
        text = open(csv_file, 'r')
        return text.read()

    def term_freq(self, term, doc):
        text = self._read_text(doc)
        return text.count(term)

    def tf_log(self, term, doc):
        freq = self.term_freq(term, doc)
        if freq > 0:
            return 1 + math.log10(freq)
        else:
            return 0
    
    def tf_square(self, term, doc):
        tlog = self.tf_log(term, doc)
        return tlog ** 2
    
    def tf_norm(self, term, doc):
        tbull = self.tf_log(term, 'bull')
        tbear = self.tf_log(term, 'bear')
        tneut = self.tf_log(term, 'neut')

        tbull_sq = self.tf_square(term, 'bull')
        tbear_sq = self.tf_square(term, 'bear')
        tneut_sq = self.tf_square(term, 'neut')

        sum_denom = math.sqrt(tbull_sq + tbear_sq + tneut_sq)

        if 'bull' in doc:
            return tbull / sum_denom
        elif 'bear' in doc:
            return tbear / sum_denom
        else:
            return tneut / sum_denom

    def idf(self, term, doc):
        