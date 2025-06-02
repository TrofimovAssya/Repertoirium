import pandas as pd
import pickle
from collections import defaultdict

def generate_masked_variants(seq):
    return [seq[:i] + "*" + seq[i+1:] for i in range(len(seq))]

df = pd.read_csv("tcr_data.csv")
df = df.dropna(subset=["cdr3_sequence"])

masked_index = defaultdict(set)
for i, row in df.iterrows():
    seq = row["cdr3_sequence"]
    if isinstance(seq, str):
        for mv in generate_masked_variants(seq):
            masked_index[(len(seq), mv)].add(i)

with open("tcr_data_masked_index.pkl", "wb") as f:
    pickle.dump(masked_index, f)
