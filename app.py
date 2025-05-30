import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="TCR Browser", layout="wide")

# Title
st.title("🧬 TCR Sequence Explorer")

# File upload
uploaded_file = st.file_uploader("Upload a TCR CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("tcr_data.csv")

# Clean column names
df.columns = [col.strip().lower() for col in df.columns]

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    search = st.text_input("Search CDR3 sequence (partial or full)")
    one_letter_diff = st.checkbox("Include sequences differing by exactly one letter")
    chain = st.selectbox("Chain type", ["All"] + sorted(df['chain'].dropna().unique().tolist()))
    organism = st.selectbox("Organism", ["All"] + sorted(df['organism'].dropna().unique().tolist()))
    condition = st.selectbox("Condition", ["All"] + sorted(df['condition'].dropna().unique().tolist()))
    peptide = st.selectbox("Peptide", ["All"] + sorted(df['peptide'].dropna().unique().tolist()))

# Apply filters
filtered = df.copy()
if chain != "All":
    filtered = filtered[filtered['chain'] == chain]
if organism != "All":
    filtered = filtered[filtered['organism'] == organism]
if condition != "All":
    filtered = filtered[filtered['condition'] == condition]
if peptide != "All":
    filtered = filtered[filtered['peptide'] == peptide]

def build_mask_index(seq_list):
    mask_index = defaultdict(list)
    for seq in seq_list:
        for i in range(len(seq)):
            masked = seq[:i] + '*' + seq[i+1:]
            mask_index[masked].append(seq)
    return mask_index

def find_one_letter_diff(seq_list, target_seq, mask_index=None):
    if mask_index is None:
        mask_index = build_mask_index(seq_list)
    candidates = set()
    for i in range(len(target_seq)):
        masked = target_seq[:i] + '*' + target_seq[i+1:]
        for seq in mask_index.get(masked, []):
            # Check exactly one letter difference
            if len(seq) == len(target_seq):
                diff_count = sum(1 for a, b in zip(seq, target_seq) if a != b)
                if diff_count == 1:
                    candidates.add(seq)
    return candidates

# If searching and checkbox is enabled
if search and one_letter_diff:
    # First filter sequences of the same length as search to build index (for speed)
    seqs_same_len = filtered[filtered['cdr3_sequence'].str.len() == len(search)]['cdr3_sequence'].unique().tolist()
    mask_index = build_mask_index(seqs_same_len)
    near_seqs = find_one_letter_diff(seqs_same_len, search, mask_index)
    
    # Also include exact or partial matches in filtered by search substring
    filtered_search = filtered[filtered['cdr3_sequence'].str.contains(search, case=False, na=False)]
    
    # Combine the dataframe rows for sequences found by near match and substring match
    filtered_near = filtered[filtered['cdr3_sequence'].isin(near_seqs)]
    
    # Union results (avoid duplicates)
    filtered = pd.concat([filtered_search, filtered_near]).drop_duplicates().reset_index(drop=True)

elif search:
    filtered = filtered[filtered['cdr3_sequence'].str.contains(search, case=False, na=False)]

# Display results
st.subheader(f"🔬 Showing {len(filtered)} result(s)")
if "pubmed_id" in filtered.columns:
    filtered["PubMed Link"] = filtered["pubmed_id"].apply(
        lambda x: f"[{int(x)}](https://pubmed.ncbi.nlm.nih.gov/{int(x)})" if pd.notna(x) else ""
    )
st.dataframe(filtered, use_container_width=True)

# Download button
st.download_button("📥 Download filtered data", filtered.to_csv(index=False), "filtered_tcrs.csv", "text/csv")
