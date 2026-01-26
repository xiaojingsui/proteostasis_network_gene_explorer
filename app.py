import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# 2. Custom CSS for Perfectly Aligned Light Cyan Theme
st.markdown("""
    <style>
    /* Background and Global Styles */
    .stApp {
        background-color: #E0F7FA; 
    }
    
    /* Hero Section Alignment */
    .hero-section {
        padding: 40px 0px 20px 0px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .hero-title {
        font-size: 52px !important;
        font-weight: 800;
        margin-bottom: 5px;
        text-transform: uppercase;
        color: #00838F;
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: #006064;
        margin-bottom: 25px;
    }

    /* Fixed Search Bar Alignment */
    div.stTextInput {
        width: 100% !important;
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    div.stTextInput > div > div > input {
        border-radius: 25px;
        height: 50px;
        padding-left: 25px;
        font-size: 16px;
        border: 2px solid #4DD0E1;
        background-color: white;
    }

    /* Suggestion Chips Alignment */
    .suggestion-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-top: 15px;
        font-size: 14px;
        color: #006064;
    }
    
    .chip {
        background: #B2EBF2;
        padding: 4px 15px;
        border-radius: 20px;
        color: #006064;
        font-weight: 500;
    }

    /* Table Styling: Remove first column and borders */
    .result-container {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        width: 100%;
        border-collapse: collapse;
        border: none !important;
    }
    
    th {
        background-color: #B2EBF2 !important;
        color: #006064 !important;
        text-align: left !important;
        padding: 15px !important;
        border: none !important;
    }
    
    td {
        padding: 15px !important;
        border-bottom: 1px solid #E0F2F1 !important;
    }

    /* Hide the automatic Streamlit Index Column */
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
        # Sheet name from user input
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        # Filter for valid entries
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. Main Interface
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search Bar Container
search_query = st.text_input("", placeholder="Search by Gene Symbol, UniProt ID, or Branch...", label_visibility="collapsed").strip()

# Centered Suggestions
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
        st.write(f"**{len(results)} results found for '{search_query}'**")
        
        # Hyperlink UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank" style="color: #00838F; font-weight: bold; text-decoration: none;">{x}</a>'
        )
        
        # Final Column Selection
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group']]
        
        # Render HTML table to enforce CSS styling and hide index
        st.write(
            display_df.to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error("No results found. Please try another search term.")

# Footer info
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")