import pandas as pd
import numpy as np

# Open the test
df = pd.read_csv('output/test_sample.csv', index_col=0)

# We have to sort by the future trend
# Bearish
br = df[df['future'] == 'BR']
# Neutral
nt = df[df['future'] == 'NT']
# Bullish
bl = df[df['future'] == 'BL']

# Now write them in separate csv files.
br.to_csv('output/bearish_sample.csv', index=False)
nt.to_csv('output/neutral_sample.csv', index=False)
bl.to_csv('output/bullish_sample.csv', index=False)
