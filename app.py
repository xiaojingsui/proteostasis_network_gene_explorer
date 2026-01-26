import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# 2. Custom CSS (Spacious, Cyan Theme)
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
    }
    /* Centering and sizing the search input container */
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
    }
    /* Table Styling */
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        border-collapse: collapse;
        margin-top: 40px;
    }
    th { background-color: #F0FBFC !important; color: #006064 !important; text-align: left !important; padding: 18px !important; }
    td { padding: 18px !important; border-bottom: 1px solid #F0F0F0 !important; }
    thead tr th:first-child, tbody tr td:first-child { display: none; }
    
    /* Button Styling to look like chips */
    .stButton>button {
        background-color: #B2EBF2 !important;
        color: #006064 !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 5px 20px !important;
    }
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

# 4. Interface Logic
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Important: The search input uses 'search_key' to stay synced
search_query = st.text_input(
    "", 
    placeholder="Search by Gene Symbol, UniProt ID, or Branch...", 
    label_visibility="collapsed",
    key="search_key"
).strip()

# 5. Clickable Chips Section
col_label, col1, col2, col3 = st.columns([2, 1, 1, 1.5])
with col_label:
    st.markdown("<p style='text-align:right; font-size:18px; color:#006064; padding-top:5px;'>Try searching for:</p>", unsafe_allow_html=True)

with col1:
    if st.button("HSPA1A"):
        st.session_state.search_key = "HSPA1A"
        st.rerun()

with col2:
    if st.button("P0DMV8"):
        st.session_state.search_key = "P0DMV8"
        st.rerun()

with col3:
    if st.button("Chaperone"):
        st.session_state.search_key = "Chaperone"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 6. Search and Results
if st.session_state.search_key:
    query = st.session_state.search_key
    results = df[
        df['Gene Symbol'].astype(str).str.contains(query, case=False, na=False) | 
        df['UniProt ID'].astype(str).str.contains(query, case=False, na=False) |
        df['Branch'].astype(str).str.contains(query, case=False, na=False)
    ].copy()
    
    if not results.empty:
        st.markdown(f"#### {len(results)} results found for '{query}'")
        
        # Hyperlink UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank" style="color: #00838F; font-weight: bold; text-decoration: none;">{x}</a>'
        )
        
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group']]
        st.write(
            display_df.to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error(f"No results found for '{query}'.")

# Footer
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")