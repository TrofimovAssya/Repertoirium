import streamlit as st
import pandas as pd
import pickle
from collections import defaultdict

st.set_page_config(page_title="TCR Browser", layout="wide")

# Utility to create masked variants of a sequence
def generate_masked_variants(seq):
    return [seq[:i] + "*" + seq[i+1:] for i in range(len(seq))]

# Load dataset
DATA_FILE = "tcr_data.csv"
MASKED_INDEX_FILE = "tcr_data_masked_index.pkl"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df.columns = [col.strip().lower() for col in df.columns]
    df.dropna(subset=["cdr3_sequence"], inplace=True)
    return df

@st.cache_resource
def load_masked_index():
    with open(MASKED_INDEX_FILE, "rb") as f:
        return pickle.load(f)

df = load_data()
masked_index = load_masked_index()

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    search = st.text_input("Search CDR3 sequence (exact or 1 mismatch)")
    use_masked_search = st.checkbox("Use optimized 1 mismatch search?", value=True)
    chain = st.selectbox("Chain type", ["All"] + sorted(df['chain'].dropna().unique().tolist()))
    organism = st.selectbox("Organism", ["All"] + sorted(df['organism'].dropna().unique().tolist()))
    condition = st.selectbox("Condition", ["All"] + sorted(df['condition'].dropna().unique().tolist()))
    peptide = st.selectbox("Peptide", ["All"] + sorted(df['peptide'].dropna().unique().tolist()))

# Apply filters
filtered = df.copy()
if search:
    if use_masked_search:
        masked_variants = generate_masked_variants(search)
        matching_indices = set()
        for mv in masked_variants:
            matching_indices.update(masked_index.get((len(search), mv), []))
        #filtered = filtered.loc[matching_indices]
        filtered = filtered.loc[list(matching_indices)]

    else:
        filtered = filtered[filtered['cdr3_sequence'].str.contains(search, case=False, na=False)]

if chain != "All":
    filtered = filtered[filtered['chain'] == chain]
if organism != "All":
    filtered = filtered[filtered['organism'] == organism]
if condition != "All":
    filtered = filtered[filtered['condition'] == condition]
if peptide != "All":
    filtered = filtered[filtered['peptide'] == peptide]

# Display results
st.subheader(f"🔬 Showing {len(filtered)} result(s)")
if "pubmed_id" in filtered.columns:
    filtered["PubMed Link"] = filtered["pubmed_id"].apply(
        lambda x: f"[{int(x)}](https://pubmed.ncbi.nlm.nih.gov/{int(x)})" if pd.notna(x) else ""
    )
st.dataframe(filtered, use_container_width=True)

# Download button
st.download_button("📥 Download filtered data", filtered.to_csv(index=False), "filtered_tcrs.csv", "text/csv")
