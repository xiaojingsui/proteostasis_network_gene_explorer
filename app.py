import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# 2. Custom CSS for Spacious, Perfectly Aligned UI
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #E0F7FA; 
    }
    
    /* Hero Section */
    .hero-section {
        padding: 50px 0px 10px 0px;
        text-align: center;
    }
    
    .hero-title {
        font-size: 52px !important;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        color: #00838F;
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: #006064;
        margin-bottom: 40px;
    }

    /* Extra Wide and Extra Tall Search Bar */
    div[data-testid="stTextInput"] {
        width: 95% !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 15px;
        height: 80px !important; /* Increased height for better font fit */
        padding: 0px 30px !important;
        font-size: 22px !important; /* Larger font size */
        line-height: 80px !important; /* Centers text vertically */
        border: 1px solid #B2EBF2;
        border-bottom: 4px solid #4DD0E1 !important; /* Thicker cyan bottom line */
        background-color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* Suggestion Chips */
    .suggestion-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-top: 25px;
        font-size: 16px;
        color: #006064;
    }
    
    .chip {
        background: #B2EBF2;
        padding: 8px 20px;
        border-radius: 25px;
        color: #006064;
        font-weight: 500;
    }

    /* Result Table Container */
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        border-collapse: collapse;
        margin-top: 40px;
        overflow: hidden;
    }
    
    th {
        background-color: #F0FBFC !important;
        color: #006064 !important;
        text-align: left !important;
        padding: 20px !important;
        border-bottom: 2px solid #E0F7FA !important;
        font-weight: 700;
    }
    
    td {
        padding: 20px !important;
        border-bottom: 1px solid #F0F0F0 !important;
        font-size: 16px;
    }

    /* Hide Streamlit Index Column */
    thead tr th:first-child, 
    tbody tr td:first-child {
        display: none;
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

# 4. Main UI
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search Input
search_query = st.text_input("", placeholder="Search by Gene Symbol, UniProt ID, or Branch...", label_visibility="collapsed").strip()

# Suggestions
st.markdown("""
    <div class="suggestion-container">
        <span>Try searching for:</span>
        <span class="chip">HSPA1A</span>
        <span class="chip">P0DMV8</span>
        <span class="chip">Chaperone</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 5. Search Results Logic
if search_query:
    results = df[
        df['Gene Symbol'].str.contains(search_query, case=False, na=False) | 
        df['UniProt ID'].str.contains(search_query, case=False, na=False) |
        df['Branch'].str.contains(search_query, case=False, na=False)
    ].copy()
    
    if not results.empty:
        st.markdown(f"#### {len(results)} results found")
        
        # Hyperlink UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank" style="color: #00838F; font-weight: bold; text-decoration: none;">{x}</a>'
        )
        
        # Display Columns
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