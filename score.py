import math
import pandas as pd

# TODO: Write documentation and do it DRY


class TfIdf(object):

    def __init__(self, fbull, fneut, fbear):
        self.bullish = fbull
        self.neutral = fneut
        self.bearish = fbear

    def get_file(self, cat):
        if 'bull' in cat.lower():
            return self.bullish
        elif 'bear' in cat.lower():
            return self.bearish
        else:
            return self.neutral

    def _read_csv(self, doc):
        csv_file = self.get_file(doc)
        df = pd.read_csv(csv_file)
        return df

    def _read_text(self, doc):
        csv_file = self.get_file(doc)
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
        """
        The IDF formula here considers that each observation or a date is a document.

        :param term: The term to search
        :param doc: The class of document: 'bull', 'bear' or 'neut'
        :return: The IDF value of the term
        """
        text = self._read_text(doc)
        count = text.count(term)
        rows = self._read_csv(doc).shape[0]
        return math.log10(rows/count)

    def idf_square(self, term, doc):
        idflog = self.idf(term, doc)
        return idflog ** 2

    def idf_norm(self, term, doc):
        tbull = self.idf(term, 'bull')
        tbear = self.idf(term, 'bear')
        tneut = self.idf(term, 'neut')

        tbull_sq = self.idf_square(term, 'bull')
        tbear_sq = self.idf_square(term, 'bear')
        tneut_sq = self.idf_square(term, 'neut')

        sum_denom = math.sqrt(tbull_sq + tbear_sq + tneut_sq)

        if 'bull' in doc:
            return tbull / sum_denom
        elif 'bear' in doc:
            return tbear / sum_denom
        else:
            return tneut / sum_denom
