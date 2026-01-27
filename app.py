import streamlit as st
import pandas as pd
import re

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# CALLBACK FUNCTION
def update_search(new_query):
    st.session_state.search_key = new_query

# HELPER FUNCTION: Convert IPR IDs to Links
def link_interpro_ids(text):
    if pd.isna(text) or str(text).lower() == "(none noted)":
        return text
    ids = re.findall(r'IPR\d+', str(text))
    if not ids: return text
    linked_text = str(text)
    for ipr_id in set(ids):
        link = f'<a href="https://www.ebi.ac.uk/interpro/entry/InterPro/{ipr_id}/" target="_blank">{ipr_id}</a>'
        linked_text = linked_text.replace(ipr_id, link)
    return linked_text

# HELPER FUNCTION: Alliance of Genome Resources Link
def link_alliance_gene(gene_id):
    if pd.isna(gene_id): return gene_id
    # Format assumes IDs like HGNC:XXXX or NCBI_Gene:XXXX
    # If your Excel only has numbers, use: f"HGNC:{gene_id}" or similar logic
    return f'<a href="https://www.alliancegenome.org/gene/{gene_id}" target="_blank">{gene_id}</a>'

# 2. Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    .hero-section { padding: 60px 0px 10px 0px; text-align: center; }
    .hero-title { font-size: 52px !important; font-weight: 800; color: #00838F; }
    .hero-subtitle { font-size: 24px !important; color: #006064; margin-bottom: 40px; }
    .result-container { background-color: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 100%; margin-top: 20px; border-collapse: collapse; }
    th { background-color: #F0FBFC !important; color: #006064 !important; text-align: left !important; padding: 15px !important; }
    td { padding: 15px !important; border-bottom: 1px solid #F0F0F0 !important; font-size: 14px; }
    a { color: #00838F !important; font-weight: bold; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data()

# 4. Hero Section & Search
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)
st.text_input("", placeholder="Search genes, domains, or types...", label_visibility="collapsed", key="search_key")
st.markdown('</div>', unsafe_allow_html=True)

# 5. Logic
query = st.session_state.search_key
if query:
    mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    results = df[mask].copy()
    
    if not results.empty:
        # Transformation: UniProt Links
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
        )
        
        # Transformation: Alliance of Genome Resources Links (Gene ID)
        if 'Gene ID' in results.columns:
            results['Gene ID'] = results['Gene ID'].apply(link_alliance_gene)
        
        # Transformation: InterPro Links
        if 'Principal Domains' in results.columns:
            results['Principal Domains'] = results['Principal Domains'].apply(link_interpro_ids)
        if 'Auxiliary Domains' in results.columns:
            results['Auxiliary Domains'] = results['Auxiliary Domains'].apply(link_interpro_ids)
        
        # Display
        display_cols = ['Gene ID', 'Gene Symbol', 'UniProt ID', 'Branch', 'Class', 'Principal Domains', 'Auxiliary Domains']
        available_cols = [c for c in display_cols if c in results.columns]
        
        st.write(results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), unsafe_allow_html=True)
    else:
        st.error(f"No results found for '{query}'.")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0")