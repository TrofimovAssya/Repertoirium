# TCR Sequence Explorer (Local App)

A simple Streamlit app to browse, filter, and search TCR sequences.

## 🔧 Setup

1. **Install Python** (3.9+)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 File Formats

TCR CSV must include these columns:
- `cdr3_sequence`
- `chain` (alpha/beta)
- `organism` (e.g. Human/Mouse)
- `condition` (e.g. Healthy/Disease)
- `peptide` (optional)
- `pubmed_id` (optional)

## ✅ Features

- Search CDR3 sequences (partial match)
- Filter by chain, organism, condition, peptide
- Clickable PubMed links
- Upload new CSVs
- Download filtered results
