
import streamlit as st
import pandas as pd

st.set_page_config(page_title="TCR Browser", layout="wide")

def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        return float("inf")
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

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
    search = st.text_input("Search CDR3 sequence (partial or full or exact)")
    allow_mismatch = st.checkbox("Allow 1 amino acid mismatch (exact length only)?", value=False)
    chain = st.selectbox("Chain type", ["All"] + sorted(df['chain'].dropna().unique().tolist()))
    organism = st.selectbox("Organism", ["All"] + sorted(df['organism'].dropna().unique().tolist()))
    condition = st.selectbox("Condition", ["All"] + sorted(df['condition'].dropna().unique().tolist()))
    peptide = st.selectbox("Peptide", ["All"] + sorted(df['peptide'].dropna().unique().tolist()))

# Apply filters
filtered = df.copy()
if search:
    if allow_mismatch:
        filtered = filtered[filtered['cdr3_sequence'].apply(
            lambda x: hamming_distance(x, search) <= 1 if isinstance(x, str) and len(x) == len(search) else False)]
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
