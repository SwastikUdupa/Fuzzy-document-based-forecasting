import pandas as pd


class Classify(object):
    def __init__(self, data, out):
        """
        This class takes in the input of the processed output file and classifies it into 3 categories.
        :param data: The input CSV file
        :param out: The output folder
        """
        self.df = pd.read_csv(data, index_col=0)
        self.out = out

    def run(self):
        # We have to sort by the future trend
        # Bearish
        br = self.df[self.df['future'] == 'BR']
        # Neutral
        nt = self.df[self.df['future'] == 'NT']
        # Bullish
        bl = self.df[self.df['future'] == 'BL']

        # Before writing these to files, we need to remove the future value from the dataframe to avoid interference in
        # the scoring section.
        br = br.drop(['future'])
        nt = nt.drop(['future'])
        bl = bl.drop(['future'])

        # Now write them in separate csv files.
        br.to_csv(self.out + '/bearish_sample.csv', index=False)
        nt.to_csv(self.out + '/neutral_sample.csv', index=False)
        bl.to_csv(self.out + '/bullish_sample.csv', index=False)
