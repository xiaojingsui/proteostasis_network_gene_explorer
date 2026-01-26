import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# CALLBACK FUNCTION
def update_search(new_query):
    st.session_state.search_key = new_query

# 2. Custom CSS (Light Cyan Theme)
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    .hero-section { padding: 60px 0px 10px 0px; text-align: center; }
    .hero-title {
        font-size: 52px !important;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        color: #00838F;
    }
    .hero-subtitle {
        font-size: 24px !important;
        color: #006064;
        margin-bottom: 40px;
    }
    div[data-testid="stTextInput"] {
        width: 60% !important; 
        margin: 0 auto !important; 
    }
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 12px !important;
        padding: 22px 25px !important;
        font-size: 20px !important; 
        border: 1px solid #B2EBF2 !important;
        border-bottom: 4px solid #4DD0E1 !important;
        background-color: white !important;
    }
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        margin-top: 40px;
        border-collapse: collapse;
    }
    th { background-color: #F0FBFC !important; color: #006064 !important; text-align: left !important; padding: 15px !important; }
    td { padding: 15px !important; border-bottom: 1px solid #F0F0F0 !important; font-size: 14px; }
    
    /* Link styling */
    a { color: #00838F !important; font-weight: bold; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
    try:
        # Loading the specific sheet
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        # Drop rows where critical info is missing
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data()

# 4. Hero Section
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search Input
st.text_input(
    "", 
    placeholder="Search by Gene Symbol, UniProt ID, Branch, Type, or Subtype...", 
    label_visibility="collapsed",
    key="search_key" 
)

# 5. Quick Filter Chips
c1, c2, c3, c4 = st.columns([1.5, 0.6, 0.6, 0.8])
with c1:
    st.markdown("<p style='text-align:right; font-size: 18px; color: #006064; padding-top: 5px;'>Try searching for:</p>", unsafe_allow_html=True)
with c2:
    st.button("HSPA1A", on_click=update_search, args=("HSPA1A",))
with c3:
    st.button("P0DMV8", on_click=update_search, args=("P0DMV8",))
with c4:
    st.button("Chaperone", on_click=update_search, args=("Chaperone",))
st.markdown('</div>', unsafe_allow_html=True)

# 6. Results Logic
query = st.session_state.search_key
if query:
    # Expanded search logic to include UniProt ID and more columns from your sheet
    search_columns = ['Gene Symbol', 'UniProt ID', 'Gene Name', 'Type', 'Subtype', 'Principal Domains']
    
    # Filter the dataframe
    mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    results = df[mask].copy()
    
    if not results.empty:
        st.markdown(f"#### {len(results)} results found for '{query}'")
        
        # TRANSFORMATION: Convert UniProt ID into a clickable link
        # We wrap the ID in an <a> tag pointing to the UniProtKB entry
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprot/{x}" target="_blank">{x}</a>'
        )
        
        # Select columns for display (based on your Excel headers)
        display_cols = [
            'UniProt ID', 'Gene Symbol', 'Branch', 'Class','Group',
            'Type', 'Subtype'
        
        # Only show columns that actually exist in the dataframe
        available_cols = [c for c in display_cols if c in results.columns]
        display_df = results[available_cols]
        
        # Render Table as HTML to allow the links to function
        st.write(
            display_df.to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error(f"No results found for '{query}'.")

# Footer
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")