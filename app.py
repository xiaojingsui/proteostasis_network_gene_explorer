import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the search bar key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# CALLBACK FUNCTION: Safely updates the search bar text
def update_search(new_query):
    st.session_state.search_key = new_query

# 2. Custom CSS for Light Cyan Theme & Perfectly Aligned Layout
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
        font-size: 32px !important;
        color: #006064;
        margin-bottom: 40px;
    }

    /* Tall, Centered Search Bar (50% width) */
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

    /* Suggestion Container - Tight Grouping */
    [data-testid="column"] { width: fit-content !important; flex: unset !important; min-width: unset !important; }
    div[data-testid="stHorizontalBlock"] { justify-content: center !important; gap: 10px !important; }

    /* Button Styling */
    .stButton>button {
        background-color: #B2EBF2 !important;
        color: #006064 !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 5px 20px !important;
        font-size: 16px !important;
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

# 4. Interface Section
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search Input tied to session state
st.text_input(
    "", 
    placeholder="Search by Gene, ID, Branch, Class, Group, Type, or Subtype...", 
    label_visibility="collapsed",
    key="search_key" 
)

# 5. Clickable Chips Section
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

# 6. Search Results Logic
query = st.session_state.search_key
if query:
    # Expanded search logic to include Class, Type, and Subtype
    # "Principal Domains" remains excluded
    results = df[
        df['Gene Symbol'].astype(str).str.contains(query, case=False, na=False) | 
        df['UniProt ID'].astype(str).str.contains(query, case=False, na=False) |
        df['Branch'].astype(str).str.contains(query, case=False, na=False) |
        df['Class'].astype(str).str.contains(query, case=False, na=False) |
        df['Group'].astype(str).str.contains(query, case=False, na=False) |
        df['Type'].astype(str).str.contains(query, case=False, na=False) |
        df['Subtype'].astype(str).str.contains(query, case=False, na=False)
    ].copy()
    
    if not results.empty:
        st.markdown(f"#### {len(results)} results found for '{query}'")
        
        # Link UniProt ID
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank" style="color: #00838F; font-weight: bold; text-decoration: none;">{x}</a>'
        )
        
        # Display table columns including requested additions
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group', 'Type', 'Subtype']]
        st.write(
            display_df.to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error(f"No results found for '{query}'.")

# Footer
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")