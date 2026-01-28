import streamlit as st
import pandas as pd
import io

# 1. Page Config (Must be the first command)
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state variables
if "search_key" not in st.session_state:
    st.session_state.search_key = ""
if "page" not in st.session_state:
    st.session_state.page = "Search"

# CALLBACKS
def update_search(new_query):
    st.session_state.search_key = new_query

# 2. LOAD DATA
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 4.1 - 2026-0127.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='MAIN')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. GLOBAL CSS
st.markdown("""
    <style>
    /* --- GLOBAL FONTS & MAIN CONTAINER --- */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FBFEFF;
    }
    
    /* Remove standard top padding so the navbar sits at the very top */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* Hide standard Streamlit header elements */
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* --- CUSTOM NAVBAR (STYLING THE RADIO BUTTON) --- */
    /* 1. Make the radio group a horizontal row with a white background and bottom border */
    div[role="radiogroup"] {
    position: fixed !important;      /* 1. Sticks it to the screen */
    top: 0 !important;               /* 2. Anchors to very top */
    left: 0 !important;              /* 3. Anchors to left edge */
    width: 100vw !important;         /* 4. Forces full screen width */
    z-index: 99999 !important;       /* 5. Ensures it sits on top of everything */
    
    background-color: #000000;       /* 6. Sage green color from screenshot */
    
    display: flex !important;
    justify-content: center !important; /* 7. CENTERS the Search/About buttons */
    }

    /* 2. Hide the actual radio bubbles/circles */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* 3. Style the text labels to look like navbar links */
    div[role="radiogroup"] label {
        margin-right: 0px !important;
    }

    div[role="radiogroup"] p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #444444 !important;
        cursor: pointer;
        padding: 5px 10px;
        border-radius: 5px;
        transition: background-color 0.2s;
    }

    div[role="radiogroup"] p:hover {
        background-color: #F0FBFC;
        color: #006064 !important;
    }

    /* --- TABLE & GENERAL STYLING --- */
    td { 
        font-family: Arial, Helvetica, sans-serif !important;
        padding: 15px !important; 
        border-bottom: 1px solid #F0F0F0 !important; 
        font-size: 14px !important; 
        color: #212121 !important;
        background-color: #FFFFFF !important;
    }

    .section-header {
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 24px !important;
        font-weight: bold !important;
        color: #006064 !important;
        margin-bottom: 10px !important;
    }

    .hero-section { padding: 40px 0px 20px 0px; text-align: center; }
    
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

    /* Input Box Styling */
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

    /* Results Table Styling */
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
    
    /* Contact Box Styling */
    .info-box {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: white;
        border: 1px solid #4DD0E1;
        border-radius: 8px;
        padding: 20px;
        height: 240px; 
        color: #006064;
    }
    
    a { color: #00838F !important; font-weight: bold; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)


# --- TOP NAVBAR (Using st.radio styled with CSS) ---
# We map the labels with icons to internal values
NAV_OPTIONS = ["🔍 Search", "ℹ️ About"]

# Place the radio button at the very top. 
# The CSS above hides the circles and makes it look like a navbar.
selected_nav = st.radio(
    "Navigation", 
    NAV_OPTIONS, 
    horizontal=True, 
    label_visibility="collapsed",
    key="nav_radio"
)

# Logic to handle page selection based on the label with icon
if "Search" in selected_nav:
    selected_page = "Search"
else:
    selected_page = "About"


# ==========================================
# PAGE 1: SEARCH
# ==========================================
if selected_page == "Search":

    df = load_data()

    # Hero Section
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

    # Chip/Button Section
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

    # Results Logic
    query = st.session_state.search_key
    if query:
        if df.empty:
             st.error("Database could not be loaded. Please check the source file.")
        else:
            mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
            results = df[mask].copy()
            
            if not results.empty:
                col_results, col_download = st.columns([7, 1])
                with col_results:
                    st.markdown(f"#### {len(results)} results found for '{query}'")
                
                with col_download:
                    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
                    csv = results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"search_results_{query}.csv",
                        mime="text/csv",
                    )
                
                # Link Formatting
                results['UniProt ID'] = results['UniProt ID'].apply(
                    lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
                )
                
                if 'Gene ID' in results.columns:
                    def create_ncbi_link(val):
                        if pd.isna(val) or val == "": return ""
                        try:
                            clean_id = str(int(float(val)))
                            return f'<a href="https://www.ncbi.nlm.nih.gov/gene/{clean_id}" target="_blank">{clean_id}</a>'
                        except:
                            return f'<a href="https://www.ncbi.nlm.nih.gov/gene/?term={val}" target="_blank">{val}</a>'
                    results['Gene ID'] = results['Gene ID'].apply(create_ncbi_link)

                def create_interpro_links(val):
                    if pd.isna(val) or str(val).strip() == "" or "(none noted)" in str(val):
                        return val
                    domains = [d.strip() for d in str(val).split(';')]
                    linked_domains = []
                    for d in domains:
                        if d.startswith('IPR'):
                            url = f"https://www.ebi.ac.uk/interpro/entry/InterPro/{d}"
                            linked_domains.append(f'<a href="{url}" target="_blank">{d}</a>')
                        else:
                            linked_domains.append(d)
                    return ", ".join(linked_domains)

                if 'Interpro Domains' in results.columns:
                    results['Interpro Domains'] = results['Interpro Domains'].apply(create_interpro_links)
                
                display_cols = [
                    'UniProt ID', 'Gene ID', 'Gene Symbol', 'Branch', 
                    'Class', 'Group', 'Type', 'Subtype', 
                    'Interpro Domains'
                ]
                available_cols = [c for c in display_cols if c in results.columns]
                
                st.write(
                    results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                    unsafe_allow_html=True
                )
            else:
                st.error(f"No results found for '{query}'.")

    # Footer/Contact
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<p class="section-header">Contact</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="border-left: 5px solid #00838F;">
            <div style="margin-bottom: 15px;">
                <strong>ALP, Chaperones, Trafficking & Organelle-specific</strong><br>
                <span style="font-size: 0.9em; color: #555;">Evan Powers: <a href="mailto:PNAnnotation@gmail.com">PNAnnotation@gmail.com</a></span>
            </div>
            <div style="margin-bottom: 15px;">
                <strong>UPS</strong><br>
                <span style="font-size: 0.9em; color: #555;">Suzanne Elsasser: <a href="mailto:suzanne_elsasser@hms.harvard.edu">suzanne_elsasser@hms.harvard.edu</a></span><br>
                <span style="font-size: 0.9em; color: #555;">Daniel Finley: <a href="mailto:daniel_finley@hms.harvard.edu">daniel_finley@hms.harvard.edu</a></span>
            </div>
            <div>
                <strong>APP Support</strong><br>
                <span style="font-size: 0.9em; color: #555;">Xiaojing Sui: <a href="mailto:xiaojing.sui@northwestern.edu">xiaojing.sui@northwestern.edu</a></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<p class="section-header">Cite</p>', unsafe_allow_html=True)
        st.markdown("""
            <div class="info-box" style="border-left: 5px solid #00838F; padding: 15px; border-radius: 5px;">
                <p style="margin-bottom: 10px; font-weight: bold;">If you use this resource, please cite:</p>
                <p style="margin-bottom: 10px; font-size: 0.9em;">
                    1. A Comprehensive Enumeration of the Human Proteostasis Network. 1. Components of Translation, Protein Folding, and Organelle-Specific Systems 
                    <a href="https://doi.org/10.1101/2022.08.30.505920" target="_blank">doi:10.1101/2022.08.30.505920</a>
                </p>
                <p style="margin-bottom: 0; font-size: 0.9em;">
                    2. A Comprehensive Enumeration of the Human Proteostasis Network. 2. Components of the Autophagy-Lysosome Pathway 
                    <a href="https://doi.org/10.1101/2023.03.22.533675" target="_blank">doi:10.1101/2023.03.22.533675</a>
                </p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")


# ==========================================
# PAGE 2: ABOUT
# ==========================================
elif selected_page == "About":
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">About the Project</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="max-width: 800px; margin: 0 auto; font-size: 18px; line-height: 1.6;">
        <p>
            The <strong>Human Proteostasis Network (PN) Database</strong> is a comprehensive knowledgebase 
            dedicated to the curation and classification of genes involved in the maintenance of proteostasis.
        </p>
        <p>This resource categorizes components involved in:</p>
        <ul>
            <li>Translation and Protein Folding</li>
            <li>Autophagy-Lysosome Pathway (ALP)</li>
            <li>Ubiquitin-Proteasome System (UPS)</li>
            <li>Organelle-Specific Systems</li>
        </ul>
        <br>
        <p class="section-header">Methodology</p>
        <p>
            The data presented here is the result of extensive literature review and manual annotation 
            to ensure high-fidelity classification of protein functions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")