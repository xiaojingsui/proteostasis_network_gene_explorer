import streamlit as st
import pandas as pd
import io

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# CALLBACK FUNCTION
def update_search(new_query):
    st.session_state.search_key = new_query

# 2. Custom CSS
st.markdown("""
    <style>
    /* Set global font to Arial */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FBFEFF;
    }

    /* Hide the Streamlit header (the three dots) and footer */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Optional: Remove the padding at the top that the header used to occupy */
    .stAppDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}

    .section-header {
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 24px !important;
    font-weight: bold !important;
    color: #006064 !important;
    margin-bottom: 10px !important;
    }

    h4 {
    font-family: Arial, Helvetica, sans-serif !important;
    font-weight: 700 !important;
    color: #333333 !important;
    } 

    .hero-section { padding: 5px 0px 10px 0px; text-align: center; }
    
    .hero-title {
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 46px !important;
        font-weight: 800;
        margin-bottom: 20px;
        text-transform: uppercase;
        color: #000000;
    }
    
    .hero-subtitle {
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 24px !important;
        color: #006064;
        margin-bottom: 40px;
    }

    div[data-testid="stTextInput"] {
        width: 50% !important;      /* 50% = Half screen width. 100% = Full width. */
        min-width: 300px;
        margin: 0 auto -15px !important;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        min-height: 75px !important; /* Must be larger than your input height (approx 68px) */
    }

    div[data-testid="stTextInput"] > div > div > input {
        font-family: Arial, Helvetica, sans-serif !important;
        border-radius: 12px !important;
        
        /* Box sizing prevents math errors with padding */
        box-sizing: border-box !important; 
        
        padding: 22px 25px !important;
        font-size: 15px !important;
        
        /* Your uniform border */
        border: 2px solid #4DD0E1 !important; 
        
        background-color: white !important;
        color: #006064 !important; /* Optional: Makes typed text match your theme */
    }

    .result-container {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        margin-top: 10px;
        border-collapse: collapse;
    }

    th { 
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #F0FBFC !important; 
        color: #006064 !important; 
        text-align: left !important; 
        padding: 15px !important; 
    }

    td { 
        font-family: Arial, Helvetica, sans-serif !important;
        padding: 15px !important; 
        border-bottom: 1px solid #F0F0F0 !important; 
        font-size: 14px; 
    }

    .info-box p {
        font-family: Arial, Helvetica, sans-serif !important;
    }

    .info-box {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: white;
        border: 1px solid #4DD0E1;
        border-radius: 8px;
        padding: 20px;
        height: 180px; /* Fixed height to keep them even */
        color: #006064;
    }
    .info-title {
        font-family: Arial, Helvetica, sans-serif !important;
        font-weight: bold;
        font-size: 40px;
        color: #00838F;
        margin-bottom: 10px;
    }
    
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
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
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
    placeholder="Search by Gene Symbol, UniProt ID, Branch, Class, Group, Type, Subtype, or Domain...", 
    label_visibility="collapsed",
    key="search_key" 
)
st.markdown('</div>', unsafe_allow_html=True)

# 5. Chip Section
st.markdown('<div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 0px;">', unsafe_allow_html=True)
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

# 6. Consolidated Results Logic
query = st.session_state.search_key
if query:
    mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    results = df[mask].copy()
    
    if not results.empty:
        # Layout for Title and Download Button
        col_results, col_download = st.columns([7, 1])
        with col_results:
            st.markdown(f"#### {len(results)} results found for '{query}'")
        
        with col_download:
            # Prepare CSV for download (using the raw data before HTML tags are added)
            st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"search_results_{query}.csv",
                mime="text/csv",
            )
        
        # --- 1. LINK: UniProt ---
        results['UniProt ID'] = results['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
        )
        
        # --- 2. LINK: NCBI Gene (using GeneID) ---
        if 'GeneID' in results.columns:
            def create_ncbi_link(val):
                if pd.isna(val) or val == "": return ""
                try:
                    clean_id = str(int(float(val)))
                    return f'<a href="https://www.ncbi.nlm.nih.gov/gene/{clean_id}" target="_blank">{clean_id}</a>'
                except:
                    return f'<a href="https://www.ncbi.nlm.nih.gov/gene/?term={val}" target="_blank">{val}</a>'
            
            results['GeneID'] = results['GeneID'].apply(create_ncbi_link)

        # --- 3. LINK: InterPro Domains (Split & Link) ---
        def create_interpro_links(val):
            if pd.isna(val) or str(val).strip() == "" or "(none noted)" in str(val):
                return val
            domains = [d.strip() for d in str(val).split(',')]
            linked_domains = []
            for d in domains:
                if d.startswith('IPR'):
                    url = f"https://www.ebi.ac.uk/interpro/entry/InterPro/{d}"
                    linked_domains.append(f'<a href="{url}" target="_blank">{d}</a>')
                else:
                    linked_domains.append(d)
            return ", ".join(linked_domains)

        if 'Principal Domains' in results.columns:
            results['Principal Domains'] = results['Principal Domains'].apply(create_interpro_links)
        
        if 'Auxiliary Domains' in results.columns:
            results['Auxiliary Domains'] = results['Auxiliary Domains'].apply(create_interpro_links)
        
        # Define display columns
        display_cols = [
            'UniProt ID', 'Gene Symbol', 'GeneID', 'Branch', 
            'Class', 'Group', 'Type', 'Subtype', 
            'Principal Domains', 'Auxiliary Domains'
        ]
        available_cols = [c for c in display_cols if c in results.columns]
        
        # Render Table as HTML
        st.write(
            results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )
    else:
        st.error(f"No results found for '{query}'.")

# 7. Contact and Citation Section
st.markdown("<br><br><hr>", unsafe_allow_html=True)
col_left, col_right = st.columns(2)

with col_left:
    # This now uses the .section-header class defined in your CSS
    st.markdown('<p class="section-header">Contact</p>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-box">
            <p style="margin: 0;">📧 <a href="mailto:proteostasisconsortium@xx.edu">proteostasisconsortium@xx.edu</a></p>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="section-header">Cite</p>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-box" style="border-left: 5px solid #00838F;">
            <p style="margin: 0;">cite us</p>
        </div>
    """, unsafe_allow_html=True)
# Footer
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")