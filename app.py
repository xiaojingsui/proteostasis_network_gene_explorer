import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# 2. Custom CSS for PhaSepDB-inspired Design
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #1a3a8a 0%, #2563eb 40%, #ffffff 100%);
    }
    .hero-section {
        padding: 60px 0px;
        text-align: center;
        color: white;
    }
    .hero-title {
        font-size: 56px !important;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .hero-subtitle {
        font-size: 20px;
        opacity: 0.9;
        margin-bottom: 30px;
    }
    /* Centered Search Bar styling */
    div.stTextInput > div > div > input {
        border-radius: 25px;
        height: 50px;
        padding-left: 20px;
        font-size: 18px;
    }
    /* Result Table Container */
    .result-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
    try:
        # Loading the specific tab mentioned in your file
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        # Cleaning rows based on Gene Symbol
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. Hero Header Section
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostanis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Centered Search Bar
search_col1, search_col2, search_col3 = st.columns([1, 3, 1])
with search_col2:
    search_query = st.text_input("", placeholder="Search by Gene Symbol, UniProt ID, or Branch...", label_visibility="collapsed").strip()
st.markdown('</div>', unsafe_allow_html=True)

# 5. Search Logic & Table Display
if search_query:
    # Fuzzy matching logic
    results = df[
        df['Gene Symbol'].str.contains(search_query, case=False, na=False) | 
        df['UniProt ID'].str.contains(search_query, case=False, na=False) |
        df['Branch'].str.contains(search_query, case=False, na=False)
    ].copy()
    
    if not results.empty:
        st.markdown(f"### Search Results for \"{search_query}\"")
        st.write(f"{len(results)} results found")
        
        # Create Hyperlink for UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
        )
        
        # Select and order columns as per requested design
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group']]
        
        # Render Table without the first (index) column
        st.write(
            display_df.to_html(escape=False, index=False, justify='left', border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
        
        if st.button("Clear Search"):
            st.rerun()
    else:
        st.error("No results found. Please try another search term.")
else:
    # Example suggestions like the original design
    st.markdown("""
        <div style='text-align:center; color:white; margin-top:-20px;'>
            <p>Try searching for: 
            <span style='background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:15px; margin:0 5px;'>HSPA1A</span>
            <span style='background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:15px; margin:0 5px;'>P0DMV8</span>
            <span style='background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:15px; margin:0 5px;'>Chaperone</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

# Footer info
st.markdown("---")
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")