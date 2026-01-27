import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# 2. Custom CSS (Global)
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    
    /* Hero Section Styles */
    .hero-section { padding: 40px 0px 10px 0px; text-align: center; }
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
    
    /* Input Styling */
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
    
    /* Table Styling */
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        margin-top: 20px;
        border-collapse: collapse;
    }
    th { background-color: #F0FBFC !important; color: #006064 !important; text-align: left !important; padding: 15px !important; }
    td { padding: 15px !important; border-bottom: 1px solid #F0F0F0 !important; font-size: 14px; }
    
    /* Link styling */
    a { color: #00838F !important; font-weight: bold; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data Function
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
    try:
        # Load specific sheet
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        # Clean data: drop rows where essential identifiers are missing
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data()

# 4. Navigation Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Search Database", "Download Data"])

# ==========================================
# PAGE 1: SEARCH DATABASE
# ==========================================
if page == "Search Database":
    
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

    # Search Logic
    def update_search(new_query):
        st.session_state.search_key = new_query

    st.text_input(
        "", 
        placeholder="Search by Gene Symbol, UniProt ID, Branch, Class, Group, Type, Subtype, or Domain...", 
        label_visibility="collapsed",
        key="search_key" 
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Chip/Button Section
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
    _, c_label, c1, c2, c3, _ = st.columns([1.5, 1.2, 0.5, 0.5, 0.6, 2])

    with c_label:
        st.markdown("<p style='text-align:right; font-size: 18px; color: #006064; margin-top: 5px;'>Try searching for:</p>", unsafe_allow_html=True)
    with c1:
        st.button("HSPA1A", on_click=update_search, args=("HSPA1A",))
    with c2:
        st.button("P0DMV8", on_click=update_search, args=("P0DMV8",))
    with c3:
        st.button("Chaperone", on_click=update_search, args=("Chaperone",))
    st.markdown('</div>', unsafe_allow_html=True)

    # Results Logic
    query = st.session_state.search_key
    if query:
        # Global Search Mask
        mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        results = df[mask].copy()
        
        if not results.empty:
            st.markdown(f"#### {len(results)} results found for '{query}'")
            
            # --- 1. LINK: UniProt ---
            results['UniProt ID'] = results['UniProt ID'].apply(
                lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
            )
            
            # --- 2. LINK: NCBI Gene (using GeneID) ---
            if 'GeneID' in results.columns:
                def create_ncbi_link(val):
                    if pd.isna(val) or val == "": return ""
                    try:
                        # Clean ID: convert 3303.0 -> 3303 -> "3303"
                        clean_id = str(int(float(val)))
                        return f'<a href="https://www.ncbi.nlm.nih.gov/gene/{clean_id}" target="_blank">{clean_id}</a>'
                    except:
                        return f'<a href="https://www.ncbi.nlm.nih.gov/gene/?term={val}" target="_blank">{val}</a>'
                
                results['GeneID'] = results['GeneID'].apply(create_ncbi_link)

            # --- 3. LINK: InterPro Domains (Split & Link) ---
            def create_interpro_links(val):
                if pd.isna(val) or str(val).strip() == "" or "(none noted)" in str(val):
                    return val
                
                # Split by comma
                domains = [d.strip() for d in str(val).split(',')]
                linked_domains = []
                
                for d in domains:
                    if d.startswith('IPR'):
                        url = f"https://www.ebi.ac.uk/interpro/entry/InterPro/{d}"
                        linked_domains.append(f'<a href="{url}" target="_blank">{d}</a>')
                    else:
                        linked_domains.append(d)
                
                return ", ".join(linked_domains)

            # Apply domain linking
            if 'Principal Domains' in results.columns:
                results['Principal Domains'] = results['Principal Domains'].apply(create_interpro_links)
            
            if 'Auxiliary Domains' in results.columns:
                results['Auxiliary Domains'] = results['Auxiliary Domains'].apply(create_interpro_links)
            
            # Display Columns
            display_cols = [
                'UniProt ID', 'Gene Symbol', 'GeneID', 'Branch', 
                'Class', 'Group', 'Type', 'Subtype', 
                'Principal Domains', 'Auxiliary Domains'
            ]
            available_cols = [c for c in display_cols if c in results.columns]
            
            # Render HTML Table
            st.write(
                results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                unsafe_allow_html=True
            )
        else:
            st.error(f"No results found for '{query}'.")

# ==========================================
# PAGE 2: DOWNLOAD DATA
# ==========================================
elif page == "Download Data":
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Download Dataset</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Access the original source file for your own analysis</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.info("Preview of the data (First 10 rows):")
        st.dataframe(df.head(10))
        
    with c2:
        st.write("### Get the full dataset")
        st.write("Click the button below to download the original Excel file used to power this database.")
        
        # Read the original file into bytes
        file_name = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
        try:
            with open(file_name, "rb") as f:
                btn = st.download_button(
                    label="📥 Download Original Excel File",
                    data=f,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.error("The source file could not be found on the server.")

# Footer (Global)
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")