import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the search query if it doesn't exist
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Function to update search from chips
def set_search(query):
    st.session_state.search_query = query

# 2. Custom CSS for Centered, Tall UI with Large Subtitle
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
        font-size: 36px !important;
        color: #006064;
        margin-bottom: 50px;
        font-weight: 400;
    }
    div[data-testid="stTextInput"] {
        width: 50% !important; 
        margin: 0 auto !important; 
    }
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 12px !important;
        padding: 22px 25px !important;
        font-size: 20px !important; 
        border: 1px solid #B2EBF2 !important;
        border-bottom: 4px solid #4DD0E1 !important;
        background-color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    /* Suggestion styling */
    .suggestion-text {
        font-size: 18px;
        color: #006064;
        margin-right: 15px;
    }
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        border-collapse: collapse;
        margin-top: 40px;
    }
    th {
        background-color: #F0FBFC !important;
        color: #006064 !important;
        text-align: left !important;
        padding: 18px !important;
        border-bottom: 2px solid #E0F7FA !important;
    }
    td { padding: 18px !important; border-bottom: 1px solid #F0F0F0 !important; }
    thead tr th:first-child, tbody tr td:first-child { display: none; }
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
    except:
        return pd.DataFrame()

df = load_data()

# 4. Main Interface
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search Input tied to session state
search_input = st.text_input(
    "", 
    value=st.session_state.search_query,
    placeholder="Search by Gene Symbol, UniProt ID, or Branch...", 
    label_visibility="collapsed",
    key="main_search"
).strip()

# Update session state if user types manually
if search_input != st.session_state.search_query:
    st.session_state.search_query = search_input

# 5. Clickable Suggestion Chips
col_space, col_label, col1, col2, col3, col_space2 = st.columns([2, 1, 0.8, 0.8, 1, 2])

with col_label:
    st.write("Try searching for:")

with col1:
    if st.button("HSPA1A"):
        set_search("HSPA1A")
        st.rerun()

with col2:
    if st.button("P0DMV8"):
        set_search("P0DMV8")
        st.rerun()

with col3:
    if st.button("Chaperone"):
        set_search("Chaperone")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 6. Results Logic
current_query = st.session_state.search_query
if current_query:
    results = df[
        df['Gene Symbol'].astype(str).str.contains(current_query, case=False, na=False) | 
        df['UniProt ID'].astype(str).str.contains(current_query, case=False, na=False) |
        df['Branch'].astype(str).str.contains(current_query, case=False, na=False)
    ].copy()
    
    if not results.empty:
        st.markdown(f"#### {len(results)} results found for '{current_query}'")
        
        # Link UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank" style="color: #00838F; font-weight: bold; text-decoration: none;">{x}</a>'
        )
        
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group']]
        st.write(
            display_df.to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error("No results found. Please try another search term.")

# Footer
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")