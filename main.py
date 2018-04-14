from .fuzzification import Fuzzify
from .score import TfIdf
from .sort import Classify


if __name__ == '__main__':
    f = Fuzzify('data/sample.csv', 'output/test_sample.csv')
    f.run()
    c = Classify('output/test_sample.csv', 'output')
    c.run()
