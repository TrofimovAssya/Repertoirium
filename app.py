import streamlit as st
import pandas as pd

st.set_page_config(page_title="TCR Browser", layout="wide")
st.title("🧬 TCR Sequence Explorer")

# File upload
uploaded_file = st.file_uploader("Upload a TCR CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("tcr_data.csv")

# Clean column names & uppercase sequences
df.columns = [col.strip().lower() for col in df.columns]
df['cdr3_sequence'] = df['cdr3_sequence'].str.upper()

# Sidebar filters
with st.sidebar:
    search = st.text_input("Search CDR3 sequence (exact length)")
    one_letter_diff = st.checkbox("Include sequences differing by exactly one letter")
    chain = st.selectbox("Chain type", ["All"] + sorted(df['chain'].dropna().unique().tolist()))
    organism = st.selectbox("Organism", ["All"] + sorted(df['organism'].dropna().unique().tolist()))
    condition = st.selectbox("Condition", ["All"] + sorted(df['condition'].dropna().unique().tolist()))
    peptide = st.selectbox("Peptide", ["All"] + sorted(df['peptide'].dropna().unique().tolist()))

# Apply non-search filters first
filtered = df.copy()
if chain != "All":
    filtered = filtered[filtered['chain'] == chain]
if organism != "All":
    filtered = filtered[filtered['organism'] == organism]
if condition != "All":
    filtered = filtered[filtered['condition'] == condition]
if peptide != "All":
    filtered = filtered[filtered['peptide'] == peptide]

# Function to find sequences differing by exactly one letter or exact match
def one_letter_diff_search(sequences, query):
    results = []
    query = query.upper().strip()
    for seq in sequences:
        seq = seq.upper().strip()
        if len(seq) != len(query):
            continue
        diff_count = sum(1 for a, b in zip(seq, query) if a != b)
        if diff_count == 1 or seq == query:
            results.append(seq)
    return results

    
# Apply search filter
if search:
    search = search.upper()
    if one_letter_diff:
        all_seqs = filtered['cdr3_sequence'].unique().tolist()
        matched_seqs = one_letter_diff_search(all_seqs, search)
        filtered = filtered[filtered['cdr3_sequence'].isin(matched_seqs)]
    else:
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
