import warnings
import pandas as pd


warnings.filterwarnings('ignore')
df = pd.read_csv('data/sample.csv')

column_list = list(df.columns.values)
rows = df.shape[0]

header = ["Date", "Open Price", "High Price", "Low Price", "Close Price"]
df.to_csv('output/output_sample.csv', columns = header)

df = pd.read_csv('output/output_sample.csv', index_col=0)

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
# the average of 7 points prior to it. Not sure of this though. So we 
# avoid the first 7 points of a given dataset?


df['Candle Color'] = 0
df['Upper Shadow'] = 0
df['Lower Shadow'] = 0

df['Body'] = abs(df['Open Price']-df['Close Price'])

for i in range(rows):
    if df['Open Price'][i] > df['Close Price'][i]:
        df['Candle Color'][i] = 'Black'
        df['Upper Shadow'][i] = abs(df['Open Price'][i] - df['High Price'][i])
        df['Lower Shadow'][i] = abs(df['Close Price'][i] - df['Low Price'][i])
    else:
        df['Candle Color'][i] = 'White'
        df['Upper Shadow'][i] = abs(df['Close Price'][i] - df['High Price'][i])
        df['Lower Shadow'][i] = abs(df['Open Price'][i] - df['Low Price'][i])


df['universe_disc'] = 0
df['fMag'] = ''
df['fBody'] = ''
df['fUS'] = ''
df['fLS'] = ''
df['Bias'] = ''
df['Magnitude'] = 0
df['fm'] = ''
df['md'] = ''
# The fuzzy candlestick
df['fcs'] = ''

for i in range(rows-7):
    # 7 day moving average is the universe_disc. So skip the first 7 days.
    j = i+7
    df['universe_disc'][j] = (sum(list(df['Body'][i:j])))/7
    a = 0.15 * df['universe_disc'][j]
    b = 0.30 * df['universe_disc'][j]
    c = 0.45 * df['universe_disc'][j]
    d = 0.60 * df['universe_disc'][j]
    e = 0.75 * df['universe_disc'][j]

    # 4.1.2
    # Fuzzification of the trend of closing values before and after a particular point p in the time series

    df['Magnitude'][j] = abs(df['Close Price'][j] - df['Close Price'][j - 3])
    if df['Close Price'][j] >= df['Close Price'][j - 3]:
        df['Bias'][j] = 'Positive'
    else:
        df['Bias'][j] = 'Negative'

    # The fields fow which we need the fuzzy values.
    columns = ['Upper Shadow', 'Lower Shadow', 'Body', 'Magnitude']
    fuzzy_cols = ['fUS', 'fLS', 'fBody', 'fMag']
    fuzzy = ''
    fval = ''
    fmag = ''

    for col, fcol in zip(columns, fuzzy_cols):
        x = df[col][j]

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

        df[fcol][j] = fval

    if df['Candle Color'][j] == 'White':
        fuzzy += 'W'
    else:
        fuzzy += 'B'

    df['fcs'][j] = fuzzy

    # FMi represents the market momentum.
    #
    # There are seven rules for determining this which have been performed using the IF conditions.

    if fmag == 'TNY':
        df['fm'][j] = "Neutral"
    elif df['Bias'][j] == "Positive" and fmag == 'VS':
        df['fm'][j] = "Bullish Neutral"
    elif df['Bias'][j] == "Negative" and fmag == 'VS':
        df['fm'][j] = "Bearish Neutral"
    elif df['Bias'][j] == "Positive" and fmag == 'BG':
        df['fm'][j] = "Very Bullish"
    elif df['Bias'][j] == "Negative" and fmag == 'BG':
        df['fm'][j] = "Very Bearish"
    elif df['Bias'][j] == "Positive" and fmag == 'VB':
        df['fm'][j] = "Extremely Bullish"
    elif df['Bias'][j] == "Negative" and fmag == 'VB':
        df['fm'][j] = "Extremely Bearish"

    if df['fm'][j] == "Bearish Neutral" or df['fm'][j] == "Extremely Bearish" or df['fm'][j] == 'Very Bearish':
        df['md'][j] = 'BR'
    elif df['fm'][j] == "Bullish Neutral" or df['fm'][j] == "Very Bullish" or df['fm'][j] == "Extremely Bullish":
        df['md'][j] = 'BL'
    else:
        df['md'][j] = 'NT'

# Now to put the future trend, we need to shift the 'md' column 3 rows upward so that we get the future trend.
df['future'] = df['md']
df.future = df.future.shift(-3)

    
df.to_csv('output/test_sample.csv')
