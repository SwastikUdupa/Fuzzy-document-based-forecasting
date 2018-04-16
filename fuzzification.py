import warnings
import pandas as pd
warnings.filterwarnings('ignore')


class Fuzzify(object):
    def __init__(self, data, save):
        """
        This class takes in the data in CSV format and outputs a data in CSV format which has fuzzified Candlestick and
        the past and the future trend on that particular day.

        :param data: The input CSV file
        :param save: The location to save the output
        """
        self.df = pd.read_csv(data)
        self.save = save

    def run(self):
        """
        This function does everything in one shot. TODO: Break this function down.
        :return: None
        """
        rows = self.df.shape[0]
        header = ["Date", "Open Price", "High Price", "Low Price", "Close Price"]
        self.df.to_csv('output/temp_sample.csv', columns=header)

        self.df = pd.read_csv('output/temp_sample.csv', index_col=0)

        # From the above data, we get the following
        # 1. Upper Shadow
        # 2. Body
        # 3. Lower Shadow
        # 4. Candle Color
        #
        # For observations taken on each day.
        #
        # Upper Shadow
        # Size of the upper Shadow represents the sentiment of the buyers.
        #
        # Body
        # Body represents the intensity of the market sentiment.
        #
        # Lower Shadow
        # Size of the lower shadow represents the sentiment of the sellers.
        #
        # Candle Color
        # Shows whether the sentiment is gaining strength or losing.

        # Assumption
        #
        # The value of n to determine the universe of discourse is told to be 7.
        # Here I have assumed that, the universe of discourse for any point is
        # the average of 7 points prior to it.

        self.df['Candle Color'] = 0
        self.df['Upper Shadow'] = 0
        self.df['Lower Shadow'] = 0

        self.df['Body'] = abs(self.df['Open Price']-self.df['Close Price'])

        for i in range(rows):
            if self.df['Open Price'][i] > self.df['Close Price'][i]:
                self.df['Candle Color'][i] = 'Black'
                self.df['Upper Shadow'][i] = abs(self.df['Open Price'][i] - self.df['High Price'][i])
                self.df['Lower Shadow'][i] = abs(self.df['Close Price'][i] - self.df['Low Price'][i])
            else:
                self.df['Candle Color'][i] = 'White'
                self.df['Upper Shadow'][i] = abs(self.df['Close Price'][i] - self.df['High Price'][i])
                self.df['Lower Shadow'][i] = abs(self.df['Open Price'][i] - self.df['Low Price'][i])

        self.df['universe_disc'] = 0
        self.df['fMag'] = ''
        self.df['fBody'] = ''
        self.df['fUS'] = ''
        self.df['fLS'] = ''
        self.df['Bias'] = ''
        self.df['Magnitude'] = 0
        self.df['fm'] = ''
        self.df['md'] = ''
        # The fuzzy candlestick
        self.df['fcs'] = ''

        for i in range(rows-7):
            # 7 day moving average is the universe_disc. So skip the first 7 days.
            j = i+7
            self.df['universe_disc'][j] = (sum(list(self.df['Body'][i:j])))/7
            a = 0.15 * self.df['universe_disc'][j]
            b = 0.30 * self.df['universe_disc'][j]
            c = 0.45 * self.df['universe_disc'][j]
            d = 0.60 * self.df['universe_disc'][j]
            e = 0.75 * self.df['universe_disc'][j]

            # 4.1.2
            # Fuzzification of the trend of closing values before and after a particular point p in the time series

            self.df['Magnitude'][j] = abs(self.df['Close Price'][j] - self.df['Close Price'][j - 3])
            if self.df['Close Price'][j] >= self.df['Close Price'][j - 3]:
                self.df['Bias'][j] = 'Positive'
            else:
                self.df['Bias'][j] = 'Negative'

            # The fields fow which we need the fuzzy values.
            columns = ['Upper Shadow', 'Lower Shadow', 'Body', 'Magnitude']
            fuzzy_cols = ['fUS', 'fLS', 'fBody', 'fMag']
            fuzzy = ''
            fval = ''
            fmag = ''

            for col, fcol in zip(columns, fuzzy_cols):
                x = self.df[col][j]

                if x <= a:
                    mTNY = 1
                elif a < x < b:
                    mTNY = (b - x) / (b - a)
                else:
                    mTNY = 0

                if x == b:
                    mVS = 1
                elif a < x < b:
                    mVS = (x - a) / (b - a)
                elif b < x < c:
                    mVS = (c - x) / (c - b)
                else:
                    mVS = 0

                if x == c:
                    mSM = 1
                elif b < x < c:
                    mSM = (x - b) / (c - b)
                elif c < x < d:
                    mSM = (d - x) / (d - c)
                else:
                    mSM = 0

                if x == d:
                    mBG = 1
                elif c < x < d:
                    mBG = (x - c) / (d - c)
                elif d < x < e:
                    mBG = (e - x) / (e - d)
                else:
                    mBG = 0

                if x >= e:
                    mVB = 1
                elif d < x < e:
                    mVB = (x - d) / (b - a)
                else:
                    mVB = 0

                # Now, find the Fuzzy value
                max_val = max(mTNY, mSM, mVS, mBG, mVB)
                if mTNY == max_val:
                    fval = 'TNY'
                elif mVS == max_val:
                    fval = 'VS'
                elif mSM == max_val:
                    fval = 'SM'
                elif mBG == max_val:
                    fval = 'BG'
                else:
                    fval = 'VB'

                if fcol == 'fMag':
                    fmag = fval
                else:
                    fuzzy += fval
                # Add it to a separate col. For the reference anyway

                self.df[fcol][j] = fval

            if self.df['Candle Color'][j] == 'White':
                fuzzy += 'W'
            else:
                fuzzy += 'B'

            self.df['fcs'][j] = fuzzy

            # FMi represents the market momentum.
            #
            # There are seven rules for determining this which have been performed using the IF conditions.

            if fmag == 'TNY':
                self.df['fm'][j] = "Neutral"
            elif self.df['Bias'][j] == "Positive" and fmag == 'VS':
                self.df['fm'][j] = "Bullish Neutral"
            elif self.df['Bias'][j] == "Negative" and fmag == 'VS':
                self.df['fm'][j] = "Bearish Neutral"
            elif self.df['Bias'][j] == "Positive" and fmag == 'BG':
                self.df['fm'][j] = "Very Bullish"
            elif self.df['Bias'][j] == "Negative" and fmag == 'BG':
                self.df['fm'][j] = "Very Bearish"
            elif self.df['Bias'][j] == "Positive" and fmag == 'VB':
                self.df['fm'][j] = "Extremely Bullish"
            elif self.df['Bias'][j] == "Negative" and fmag == 'VB':
                self.df['fm'][j] = "Extremely Bearish"

            if self.df['fm'][j] == "Bearish Neutral" or self.df['fm'][j] == "Extremely Bearish" or self.df['fm'][j] == 'Very Bearish':
                self.df['md'][j] = 'BR'
            elif self.df['fm'][j] == "Bullish Neutral" or self.df['fm'][j] == "Very Bullish" or self.df['fm'][j] == "Extremely Bullish":
                self.df['md'][j] = 'BL'
            else:
                self.df['md'][j] = 'NT'

        # Now to put the future trend, we need to shift the 'md' column 3 rows upward so that we get the future trend.
        self.df['future'] = self.df['md']
        self.df.future = self.df.future.shift(-3)
        self.df.to_csv(self.save)
