import streamlit as st
import pandas as pd
import py3Dmol
from stmol import showmol
import requests

# 1. Page Configuration
st.set_page_config(page_title="PN Gene Explorer", layout="wide")

# 2. Load Data from Specific Tab
@st.cache_data
def load_data():
    # Ensure this filename matches your local file exactly
    file_path = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        # Clean data: Keep only rows with a Gene Symbol and UniProt ID
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()

# 3. Sidebar Filters
st.sidebar.title("🧬 PN Gene Explorer")

# Filter by Branch
branches = ["All"] + sorted(df['Branch'].unique().tolist())
selected_branch = st.sidebar.selectbox("Filter by Branch", branches)

# Filter by Class (dynamic based on selected branch)
if selected_branch != "All":
    class_list = ["All"] + sorted(df[df['Branch'] == selected_branch]['Class'].unique().tolist())
else:
    class_list = ["All"] + sorted(df['Class'].unique().tolist())
selected_class = st.sidebar.selectbox("Filter by Class", class_list)

# Search Box
search_query = st.sidebar.text_input("Search by Gene Symbol", "").strip().upper()

# 4. Filter Logic
filtered_df = df.copy()

if selected_branch != "All":
    filtered_df = filtered_df[filtered_df['Branch'] == selected_branch]

if selected_class != "All":
    filtered_df = filtered_df[filtered_df['Class'] == selected_class]

if search_query:
    filtered_df = filtered_df[filtered_df['Gene Symbol'].str.upper().str.contains(search_query, na=False)]

# 5. Main Interface
st.title("Proteostasis Network (PN) Gene Database")

if not filtered_df.empty:
    # Selection dropdown for the results
    gene_list = filtered_df['Gene Symbol'].unique()
    selected_gene = st.selectbox(f"Select a gene ({len(filtered_df)} found):", gene_list)
    
    selected_row = filtered_df[filtered_df['Gene Symbol'] == selected_gene].iloc[0]

    # --- Layout: Information vs 3D Structure ---
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Gene Details")
        st.subheader(selected_row['Gene Symbol'])
        st.write(f"**Gene Name:** {selected_row['Gene Name']}")
        st.write(f"**UniProt ID:** `{selected_row['UniProt ID']}`")
        
        st.info(f"**Branch:** {selected_row['Branch']}  \n"
                f"**Class:** {selected_row['Class']}  \n"
                f"**Group:** {selected_row['Group']}  \n"
                f"**Type:** {selected_row['Type']}")

        # External Links
        uniprot_id = selected_row['UniProt ID']
        st.markdown(f"[🔗 View on UniProt](https://www.uniprot.org/uniprotkb/{uniprot_id}/entry)")
        st.markdown(f"[🔗 View on AlphaFold DB](https://alphafold.ebi.ac.uk/entry/{uniprot_id})")

    with col2:
        st.header("AlphaFold 3D Structure")
        
        def render_alphafold(uid):
            # Fetching the v4 PDB file from AlphaFold DB API
            pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uid}-F1-model_v4.pdb"
            res = requests.get(pdb_url)
            if res.status_code == 200:
                view = py3Dmol.view(width=800, height=600)
                view.addModel(res.text, 'pdb')
                # Style: Rainbow spectrum (Blue to Red: N-term to C-term)
                view.setStyle({'cartoon': {'color': 'spectrum'}})
                view.zoomTo()
                return view
            return None

        with st.spinner(f"Loading 3D model for {selected_gene}..."):
            view = render_alphafold(uniprot_id)
            if view:
                showmol(view, height=600, width=800)
            else:
                st.warning("Structure not found in AlphaFold DB for this ID.")

else:
    st.warning("No genes match your current filter/search criteria.")

# Data Table Expanders
with st.expander("Show table for current selection"):
    st.dataframe(filtered_df)