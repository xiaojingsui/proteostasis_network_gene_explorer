import streamlit as st
import pandas as pd
import io
import textwrap
import requests
import math
import base64


# --- NEW: INHIBITOR DATA MAPPING ---
# Maps Gene Symbols to lists of (Name, URL)
INHIBITOR_MAP = {
    "HSP90AA1": [("AUY922", "https://www.chemicalprobes.org/luminespib?q=Hsp90"), ("BIIB021", "https://www.chemicalprobes.org/biib021?q=Hsp90"), ("Onalespib", "https://www.chemicalprobes.org/onalespib?q=Hsp90")],
    "HSP90AB1": [("AUY922", "https://www.chemicalprobes.org/luminespib?q=Hsp90"), ("BIIB021", "https://www.chemicalprobes.org/biib021?q=Hsp90"), ("Onalespib", "https://www.chemicalprobes.org/onalespib?q=Hsp90")],
    "VCP": [("CB-5083", "https://www.chemicalprobes.org/cb-5083?q=p97"), ("NMS-873", "https://www.chemicalprobes.org/nms-873?q=p97")],
    "SEC61A1": [("cotransin", "https://www.chemicalprobes.org/cotransin?q=SEC61")],
    "UBA1": [("TAK243", "https://www.chemicalprobes.org/tak-243"), ("ABP3", "https://www.chemicalprobes.org/abpa3")],
    "UBA2": [("TAK-981", "https://www.chemicalprobes.org/tak-981?q=ubiquitin")],
    "UBA3": [("pevonedistat", "https://www.chemicalprobes.org/pevonedistat")],
    "USP1": [("ML323", "https://www.chemicalprobes.org/ml323?q=USP")],
    "USP7": [("FT671", "https://www.chemicalprobes.org/ft671?q=ubiquitin")],
    "USP21": [("BAY-805", "https://www.chemicalprobes.org/bay-805?q=ubiquitin")],
    "UCHL1": [("IMP-1710", "https://www.chemicalprobes.org/imp-1710?q=ubiquitin"), ("8RK64", "https://www.chemicalprobes.org/8rk64?q=ubiquitin")],
    "PSMB9": [("KZR-504", "https://www.chemicalprobes.org/kzr-504?q=proteasome")],
    "MTOR": [("rapamycin", "https://www.chemicalprobes.org/rapamycin?q=rapamycin"), ("AZD-2014", "https://www.chemicalprobes.org/azd2014?q=rapamycin")],
    "MDM2": [("RO5353", "https://www.chemicalprobes.org/ro5353?q=MDM2"), ("MD-244", "https://www.chemicalprobes.org/md-224?q=MDM2"), ("MI-77301", "https://www.chemicalprobes.org/mi-77301?q=E3%20ligase"), ("AM-6761", "https://www.chemicalprobes.org/am-6761?q=E3%20ligase"), ("AMG232", "https://www.chemicalprobes.org/amg232?q=MDM2"), ("RO2468", "https://www.chemicalprobes.org/ro2468?q=MDM2"), ("RG7112", "https://www.chemicalprobes.org/rg7112?q=MDM2")],
    "GID4": [("PFI-7", "https://www.chemicalprobes.org/pfi-7?q=Gid4")],
    "ERN1": [("AMG-18", "https://www.chemicalprobes.org/amg-18?q=IRE1")],
    "KEAP1": [("KI-696", "https://www.chemicalprobes.org/ki-696")],
    "VHL": [("VH298", "https://www.chemicalprobes.org/vh298?q=ubiquitin")],
    "EPAS1": [("PT2399", "https://www.chemicalprobes.org/pt2399?q=HIF1a"), ("PT2385", "https://www.chemicalprobes.org/pt2385?q=HIF1a")],
    "EIF2AK3": [("AMG-PERK-44", "https://www.chemicalprobes.org/amg-perk-44?q=Unfolded"), ("GSK2656157", "https://www.chemicalprobes.org/gsk2656157?q=Unfolded")]
}

# --- HELPER FOR INHIBITOR HTML ---
def get_inhibitor_html(symbol, for_csv=False):
    inhibitors = INHIBITOR_MAP.get(symbol, [])
    if not inhibitors:
        return ""
    if for_csv:
        # Returns plain text separated by semicolon for the Excel download
        return "; ".join([name for name, url in inhibitors])
    # Returns clickable links separated by semicolon for the web UI
    return "; ".join([f'<a href="{url}" target="_blank">{name}</a>' for name, url in inhibitors])



# 1. Page Config (Must be the first command)
st.set_page_config(page_title="Human PN Annotation", layout="wide")

# Initialize session state variables
if "search_key" not in st.session_state:
    st.session_state.search_key = ""
if "page" not in st.session_state:
    st.session_state.page = "Open Search"

# CALLBACKS
def update_search(new_query):
    st.session_state.search_key = new_query

# 2. LOAD DATA
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network v4.3.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='MAIN')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        # Fill NaN in hierarchy columns with empty strings
        hierarchy_cols = ['Branch', 'Class', 'Group', 'Type', 'Subtype']
        for col in hierarchy_cols:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. HELPER FUNCTIONS
def format_links(df_input):
    """Applies HTML formatting to specific columns for display"""
    df_copy = df_input.copy()
    
    # UniProt Link
    if 'UniProt ID' in df_copy.columns:
        df_copy['UniProt ID'] = df_copy['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
        )
    
    # NCBI Gene ID Link
    if 'Gene ID' in df_copy.columns:
        def create_ncbi_link(val):
            if pd.isna(val) or val == "": return ""
            try:
                clean_id = str(int(float(val)))
                return f'<a href="https://www.ncbi.nlm.nih.gov/gene/{clean_id}" target="_blank">{clean_id}</a>'
            except:
                return f'<a href="https://www.ncbi.nlm.nih.gov/gene/?term={val}" target="_blank">{val}</a>'
        df_copy['Gene ID'] = df_copy['Gene ID'].apply(create_ncbi_link)
    
    # NEW: Add Inhibitor Column
    if 'Gene Symbol' in df_copy.columns:
        df_copy['Chemical Probes'] = df_copy['Gene Symbol'].apply(lambda x: get_inhibitor_html(x, for_csv=False))
        
    return df_copy

# -----------------------------------------------------------------------------
# FINALIZED HELPER FUNCTIONS (HANDLES RNA GENES + ROBUST API)
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def fetch_protein_names_from_api(uniprot_ids):
    """
    Fetches protein names for a list of UniProt IDs using the UniProt REST API.
    """
    if not uniprot_ids:
        return {}

    mapping = {}
    chunk_size = 50 
    chunks = [uniprot_ids[i:i + chunk_size] for i in range(0, len(uniprot_ids), chunk_size)]

    progress_bar = st.progress(0, text="Fetching protein names from UniProt...")
    total_chunks = len(chunks)
    
    for idx, chunk in enumerate(chunks):
        progress_bar.progress((idx + 1) / total_chunks, text=f"Fetching names... ({idx+1}/{total_chunks} batches)")
        
        # Double-check: ensure no empty strings in this chunk
        valid_chunk = [x for x in chunk if x and str(x).strip()]
        if not valid_chunk:
            continue

        query_parts = [f"accession:{uid}" for uid in valid_chunk]
        query = " OR ".join(query_parts)
        
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": query,
            "fields": "accession,protein_name",
            "format": "json",
            "size": 500
        }
        
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for result in data.get('results', []):
                    acc = result.get('primaryAccession')
                    name = ""
                    try:
                        name = result['proteinDescription']['recommendedName']['fullName']['value']
                    except KeyError:
                        try:
                            name = result['proteinDescription']['submissionNames'][0]['fullName']['value']
                        except:
                            name = ""
                    mapping[acc] = name
            else:
                print(f"API Error {r.status_code} for batch {idx}")
        except Exception as e:
            print(f"Connection Error for batch {idx}: {e}")
            pass
            
    progress_bar.empty()
    return mapping

def enrich_with_protein_names(df_input):
    """
    Checks if 'Protein Name' exists. If not, fetches it.
    Skips internal IDs like '(RNA gene 11)'.
    """
    df_out = df_input.copy()
    
    if 'UniProt ID' not in df_out.columns:
        return df_out

    unique_ids = df_out['UniProt ID'].unique().tolist()
    
    # --- LOGIC UPDATE: Filter out RNA genes and invalid formats ---
    clean_ids = []
    for uid in unique_ids:
        s_uid = str(uid).strip()
        # 1. Must not be empty
        # 2. Must not start with '(' (which covers your "(RNA gene ...)" cases)
        if s_uid and not s_uid.startswith('('):
            clean_ids.append(s_uid)

    if len(clean_ids) > 2500:
        df_out['Protein Name'] = "(Result set too large - Filter further to see names)"
        return df_out

    # Call API only with valid real IDs
    name_map = fetch_protein_names_from_api(clean_ids)
    
    # Apply map. If it's an RNA gene, it won't be in the map, so it returns ""
    df_out['Protein Name'] = df_out['UniProt ID'].apply(lambda x: name_map.get(str(x).strip(), ""))
    
    return df_out


# 4. GLOBAL CSS
st.markdown("""
    <style>
    /* --- GLOBAL FONTS & MAIN CONTAINER --- */
    html, body, [data-testid="stAppViewContainer"], .stApp, p, h1, h2, h3, h4, h5, h6, span, div {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FBFEFF;
        color: #212121 !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    [data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* --- CUSTOM NAVBAR --- */
    div[role="radiogroup"] {
    position: fixed !important;      
    top: 0 !important;                
    left: 0 !important;               
    width: 100vw !important;          
    z-index: 99999 !important;        
    background-color: #FFFFFF;        
    display: flex !important;
    justify-content: center !important; 
    padding: 10px 0 !important; 
    align-items: center !important; 
    border-bottom: 1px solid #E0E0E0;
    }

    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label { margin-right: 0px !important; }

    div[role="radiogroup"] p {
        font-family: Arial, Helvetica, sans-serif !important;  
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #445550 !important; 
        cursor: pointer;
        padding: 8px 20px;
        border-radius: 20px;
        transition: all 0.3s ease;
    }

    div[role="radiogroup"] p:hover {
        background-color: #F0FBFC;
        color: #006064 !important;
    }

    /* --- EXTERNAL LINK STYLING --- */
    .nav-external-link {
        position: fixed !important;
        top: 10px !important;        
        right: 40px !important;      
        z-index: 100000 !important; 
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 18px !important; 
        font-weight: 600 !important;
        color: #445550 !important;
        text-decoration: none !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;        
        padding: 8px 15px !important;
        border-radius: 20px !important; 
        transition: all 0.3s ease !important;
    }

    .nav-external-link:hover {
        background-color: #D3E8E0 !important; 
        color: #004D40 !important;
    }
    
    .nav-external-link svg {
        width: 20px !important;    
        height: 20px !important;
        fill: currentColor;
        margin-bottom: -2px;      
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
        font-size: 36px !important;
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

    /* --- WIDGET STYLING (RESTORED FROM VERSION 1) --- */
    
    /* 1. Main Container positioning */
    div[data-testid="stTextInput"] {
        width: 50% !important;      
        min-width: 300px;
        margin: 0 auto -15px !important;
    }
    
    div[data-testid="stTextInput"] > div {
        height: auto !important;
        min-height: 75px !important; 
    }

    /* 2. THE OUTER WRAPPERS (Make them Invisible) */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* 3. THE INNER INPUT (The Actual White Box) */
    div[data-testid="stTextInput"] input {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FFFFFF !important;   /* Force White Background */
        border: 2px solid #4DD0E1 !important;   /* Force Teal Border */
        border-radius: 12px !important;
        
        color: #006064 !important;              /* Force Teal Text */
        caret-color: #006064 !important;        /* Teal Cursor */
        
        box-sizing: border-box !important; 
        padding: 22px 25px !important;
        font-size: 15px !important;
    }

    /* 4. Placeholder Text */
    div[data-testid="stTextInput"] input::placeholder {
        color: #90A4AE !important;
        opacity: 1 !important;
    }

    /* 5. Focus State */
    div[data-testid="stTextInput"] input:focus {
        border-color: #006064 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* 6. HIDE INSTRUCTION TEXT (Press Enter to Apply) */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* --- DROPDOWNS --- */
    div[data-testid="stSelectbox"] * { font-family: Arial, Helvetica, sans-serif !important; }
    div[data-testid="stSelectbox"] > div > div:not([aria-disabled="true"]) {
        border-color: #E0E0E0 !important; 
        border-width: 1px !important;
        background-color: white !important;
        color: #212121 !important; 
    }
    div[data-testid="stSelectbox"]:not(:has(div[aria-disabled="true"])):hover > div > div, 
    div[data-testid="stSelectbox"]:not(:has(div[aria-disabled="true"])) > div > div:focus-within {
        border-color: #4DD0E1 !important; 
        border-width: 2px !important;
    }

    /* --- BUTTONS --- */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #212121 !important;              
        border: 1px solid #D3D3D3 !important;       
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #F0FBFC !important; 
        color: #004D40 !important;              
        border-color: #006064 !important;        
    }

    /* Results Table */
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


# --- INJECT EXTERNAL LINK ---
st.markdown("""
    <a href="https://www.proteostasisconsortium.com/pn-annotation/" target="_blank" class="nav-external-link">
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3M5 5h4v2H5v12h12v-4h2v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"></path>
        </svg>
        ProteostasisConsortium
    </a>
""", unsafe_allow_html=True)


# --- TOP NAVBAR ---
NAV_OPTIONS = ["Open Search", "Guided Search", "About", "Guides","Submission"]

selected_nav = st.radio(
    "Navigation", 
    NAV_OPTIONS, 
    horizontal=True, 
    label_visibility="collapsed",
    key="nav_radio"
)

selected_page = selected_nav


# ==========================================
# PAGE 1: OPEN SEARCH - REVISED LOGIC
# ==========================================
if selected_page == "Open Search":

    df = load_data()

    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">HUMAN Proteostasis Network Annotation</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The comprehensive annotation for human proteostasis network genes</p>', unsafe_allow_html=True)

    # Updated Placeholder to reflect new rules
    st.text_input(
        "", 
        placeholder="Search by Gene Symbol, UniProt ID, Branch, Class, Group, Type, Subtype, or InterPro Domain...", 
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

    # --- REVISED SEARCH LOGIC ---
    query = st.session_state.search_key
    if query:
        if df.empty:
             st.error("Database could not be loaded. Please check the source file.")
        else:
            # Check for Forced Exact Match syntax: 'TERM'
            is_forced_exact = query.startswith("'") and query.endswith("'")
            
            if is_forced_exact:
                # Strip the quotes for the actual search
                clean_query = query[1:-1].strip().lower()
                
                # Logic for exact match in comma-separated synonyms
                def exact_synonym_match(cell):
                    if pd.isna(cell): return False
                    # Splits by comma and checks if any item matches exactly
                    return clean_query in [item.strip().lower() for item in str(cell).split(',')]

                # Apply strict exact match across all searchable columns
                mask = (
                    (df['Gene Symbol'].str.strip().str.lower() == clean_query) |
                    (df['UniProt ID'].str.strip().str.lower() == clean_query) |
                    (df['Gene ID'].astype(str).str.strip().str.lower() == clean_query) |
                    (df['Branch'].str.strip().str.lower() == clean_query) |
                    (df['Class'].str.strip().str.lower() == clean_query) |
                    (df['Group'].str.strip().str.lower() == clean_query) |
                    (df['Type'].str.strip().str.lower() == clean_query) |
                    (df['Subtype'].str.strip().str.lower() == clean_query) |
                    (df['Gene Synonyms'].apply(exact_synonym_match))
                )
            else:
                clean_query = query.strip().lower()
                
                # 1. Partial Match: Gene Symbol and Gene Synonyms
                mask_partial = (
                    df['Gene Symbol'].str.contains(clean_query, case=False, na=False) |
                    df['Gene Synonyms'].str.contains(clean_query, case=False, na=False)
                )
                
                # 2. Exact Match: Functional terms and IDs
                # This prevents "ER" from matching "Chaperone" or "Interferon"
                functional_cols = ['UniProt ID', 'Gene ID', 'Branch', 'Class', 'Group', 'Type', 'Subtype']
                mask_exact = df[functional_cols].astype(str).apply(
                    lambda x: x.str.strip().str.lower() == clean_query
                ).any(axis=1)
                
                # 3. Interpro (List match - usually requires exact ID match)
                mask_interpro = pd.Series(False, index=df.index)
                if 'Interpro Domains' in df.columns:
                    mask_interpro = df['Interpro Domains'].apply(
                        lambda cell: clean_query in [i.strip().lower() for i in str(cell).replace(';', ',').split(',')]
                    )

                mask = mask_partial | mask_exact | mask_interpro

            results = df[mask].copy()
            
            if not results.empty:
                # ENRICH RESULTS: Add Protein Name from UniProt
                results = enrich_with_protein_names(results)

                col_results, col_download = st.columns([7, 1])
                with col_results:
                    st.markdown(f"#### {len(results)} results found for '{query}'")
                
                with col_download:
                    # Prepare a version for CSV with plain text inhibitors
                    results_csv = results.copy()
                    if 'Gene Symbol' in results_csv.columns:
                        results_csv['Chemical Probes'] = results_csv['Gene Symbol'].apply(lambda x: get_inhibitor_html(x, for_csv=True))
                    
                    dl_cols = ['UniProt ID', 'Gene ID', 'Gene Symbol', 'Gene Synonyms', 
                'Protein Name', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 
                'Chemical Probes']
                    valid_dl_cols = [c for c in dl_cols if c in results_csv.columns]
                    csv = results_csv[valid_dl_cols].to_csv(index=False).encode('utf-8')
                    st.download_button("Download CSV", data=csv, file_name=f"search_{query}.csv", mime="text/csv")
                
                
                # Format Links and Display
                results_formatted = format_links(results) # Apply the formatting with inhibitors

                # UPDATE THIS LIST
                display_cols = ['UniProt ID', 'Gene ID', 'Gene Symbol', 'Gene Synonyms', 
                'Protein Name', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 
                'Chemical Probes']
                available_cols = [c for c in display_cols if c in results_formatted.columns]

                st.write(
                    results_formatted[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"""
                    <div style="background-color: #FFFFFF; padding: 20px; border-radius: 8px; color: #E65100; border: 1px solid #FFE082; text-align: center; margin: 20px auto; width: 33%; min-width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <span style="font-size: 16px; font-weight: bold;">No results found for '{query}'</span><br>
                        <span style="font-size: 14px; color: #8D6E63;">Try using 'single quotes' for exact symbol matching.</span>
                    </div>
                """, unsafe_allow_html=True)

    # Footer Logic
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown('<p class="section-header">Contact</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="border-left: 5px solid #00838F;">
            <div style="margin-bottom: 15px;">
                <strong>ALP, Chaperones, Trafficking & Organelle-specific</strong><br>
                <span style="font-size: 0.9em; color: #555;">Evan Powers: <a href="mailto:epowers@scripps.edu">epowers@scripps.edu</a></span>
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
                <p style="margin-bottom: 10px; font-size: 0.9em;">
                    2. A Comprehensive Enumeration of the Human Proteostasis Network. 2. Components of the Autophagy-Lysosome Pathway 
                    <a href="https://doi.org/10.1101/2023.03.22.533675" target="_blank">doi:10.1101/2023.03.22.533675</a>
                </p>
                <p style="margin-bottom: 0; font-size: 0.9em;">
                    3. Survey of the human proteostasis network: the ubiquitin-proteasome system. 
                    <a href="https://doi.org/10.64898/2026.03.13.711689" target="_blank">doi:10.64898/2026.03.13.711689</a>
                </p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br><br><hr>", unsafe_allow_html=True)

    file_path = 'Human Proteostasis Network v4.3.xlsx'
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        b64 = base64.b64encode(file_data).decode()
        
        
        download_link = f'''
            <div style="margin-top: 10px; text-align: left;">
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
                   download="Human_Proteostasis_Network_v4.3.xlsx" 
                   style="font-size: 14px; color: #00838F; font-weight: bold; text-decoration: underline;">
                   Data source: Human Proteostasis Network v4.3 (Click to bulk download)
                </a>
            </div>
        '''
        st.markdown(download_link, unsafe_allow_html=True)
        
    except FileNotFoundError:
        
        st.markdown('<p style="color: #888; font-size: 14px;">Data source: Human Proteostasis Network v4.3 (File not found)</p>', unsafe_allow_html=True)


# ==========================================
# PAGE 2: GUIDED SEARCH (REVISED)
# ==========================================
elif selected_page == "Guided Search":
    df = load_data()

    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Guided Search</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Filter by hierarchy: Branch &rarr; Class &rarr; Group &rarr; Type &rarr; Subtype</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if df.empty:
        st.error("Database could not be loaded.")
    else:
        # --- HIERARCHICAL DROPDOWNS ---
        with st.container():
            # Row 1: Branch, Class, Group
            c1, c2, c3 = st.columns(3)
            
            # 1. Branch Selection
            branches = df['Branch'].unique().tolist()
            branches = [x for x in branches if x] 
            sel_branch = c1.selectbox("Select Branch", [""] + branches)

            # Logic: Filter DF based on Branch
            df_lvl1 = df[df['Branch'] == sel_branch] if sel_branch else df

            # 2. Class Selection (Depends on Branch)
            if sel_branch:
                classes = df_lvl1['Class'].unique().tolist()
                classes = [x for x in classes if x] 
                sel_class = c2.selectbox("Select Class", [""] + classes)
            else:
                sel_class = c2.selectbox("Select Class", [], disabled=True, placeholder="Select Branch first")

            # Logic: Filter DF based on Class
            df_lvl2 = df_lvl1[df_lvl1['Class'] == sel_class] if (sel_branch and sel_class) else df_lvl1

            # 3. Group Selection (Depends on Class)
            if sel_branch and sel_class:
                groups = df_lvl2['Group'].unique().tolist()
                groups = [x for x in groups if x]
                sel_group = c3.selectbox("Select Group", [""] + groups)
            else:
                sel_group = c3.selectbox("Select Group", [], disabled=True, placeholder="Select Class first")

            # Logic: Filter DF based on Group
            df_lvl3 = df_lvl2[df_lvl2['Group'] == sel_group] if (sel_branch and sel_class and sel_group) else df_lvl2

            # Row 2: Type, Subtype
            c4, c5 = st.columns(2)

            # 4. Type Selection (Depends on Group)
            if sel_branch and sel_class and sel_group:
                types = df_lvl3['Type'].unique().tolist()
                types = [x for x in types if x]
                sel_type = c4.selectbox("Select Type", [""] + types)
            else:
                sel_type = c4.selectbox("Select Type", [], disabled=True, placeholder="Select Group first")

            # Logic: Filter DF based on Type
            df_lvl4 = df_lvl3[df_lvl3['Type'] == sel_type] if (sel_branch and sel_class and sel_group and sel_type) else df_lvl3

            # 5. Subtype Selection (Depends on Type)
            if sel_branch and sel_class and sel_group and sel_type:
                subtypes = df_lvl4['Subtype'].unique().tolist()
                subtypes = [x for x in subtypes if x]
                sel_subtype = c5.selectbox("Select Subtype", [""] + subtypes)
            else:
                sel_subtype = c5.selectbox("Select Subtype", [], disabled=True, placeholder="Select Type first")
            
            # Final Filter Logic
            final_df = df_lvl4[df_lvl4['Subtype'] == sel_subtype] if (sel_branch and sel_class and sel_group and sel_type and sel_subtype) else df_lvl4

        # --- DISPLAY RESULTS (Guided Search) ---
        st.divider()

        if sel_branch:
            # 1. ENRICH RESULTS: Add Protein Name
            final_df = enrich_with_protein_names(final_df)

            col_res_header, col_res_dl = st.columns([7, 1])
            with col_res_header:
                st.markdown(f"#### Found {len(final_df)} entries")
                # ... (breadcrumb logic remains the same)

            with col_res_dl:
                st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
                
                # 2. PREPARE DOWNLOAD (Plain text inhibitors for CSV)
                df_for_dl = final_df.copy()
                if 'Gene Symbol' in df_for_dl.columns:
                    df_for_dl['Chemical Probes'] = df_for_dl['Gene Symbol'].apply(lambda x: get_inhibitor_html(x, for_csv=True))
                
                dl_cols = [
                    'UniProt ID', 'Gene ID', 'Gene Symbol', 'Gene Synonyms', 
                    'Protein Name', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 
                    'Chemical Probe'
                ]
                valid_cols = [c for c in dl_cols if c in df_for_dl.columns]
                csv = df_for_dl[valid_cols].to_csv(index=False).encode('utf-8')
                st.download_button(label="Download CSV", data=csv, file_name="guided_search_results.csv", mime="text/csv")

            # 3. PREPARE DISPLAY (HTML Links for Inhibitors)
            display_df = format_links(final_df) # This function now includes the HTML inhibitor logic
            
            # Original order + Inhibitor at the end
            display_cols = [
                'UniProt ID', 'Gene ID', 'Gene Symbol', 'Gene Synonyms', 
                'Protein Name', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 
                'Chemical Probe'
            ]
            available_cols = [c for c in display_cols if c in display_df.columns]
            
            st.write(
                display_df[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                unsafe_allow_html=True
            )
        else:
            st.markdown("""
                <div style="background-color: #E1F5FE; padding: 15px; border-radius: 8px; color: #0277BD; border: 1px solid #B3E5FC;">
                    Please select a <b>Branch</b> to begin the guided search.
                </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    file_path = 'Human Proteostasis Network v4.3.xlsx'
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        b64 = base64.b64encode(file_data).decode()
        
        
        download_link = f'''
            <div style="margin-top: 10px; text-align: left;">
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
                   download="Human_Proteostasis_Network_v4.3.xlsx" 
                   style="font-size: 14px; color: #00838F; font-weight: bold; text-decoration: underline;">
                   Data source: Human Proteostasis Network v4.3 (Click to bulk download)
                </a>
            </div>
        '''
        st.markdown(download_link, unsafe_allow_html=True)
        
    except FileNotFoundError:
        
        st.markdown('<p style="color: #888; font-size: 14px;">Data source: Human Proteostasis Network v4.3 (File not found)</p>', unsafe_allow_html=True)



# ==========================================
# PAGE 3: ABOUT
# ==========================================
elif selected_page == "About":
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">About the Project</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
<style>
.about-container {
max-width: 900px;
margin: 0 auto;
font-family: Arial, Helvetica, sans-serif !important;
font-size: 16px;
line-height: 1.6;
color: #212121;
}
.about-header {
font-size: 20px;
font-weight: bold;
color: #006064;
margin-top: 30px;
margin-bottom: 10px;
border-bottom: 2px solid #E0F7FA;
padding-bottom: 5px;
}
.term-highlight {
font-weight: bold;
color: #00838F;
}
.red-highlight {
font-weight: bold;
color: #B71C1C;
}
.about-list {
padding-left: 20px;
margin-bottom: 15px;
}
.about-list li {
margin-bottom: 8px;
}
</style>
<div class="about-container">
<p>
A more extensive description of the project can be found on the 
<a href="https://www.proteostasisconsortium.com/pn-annotation/" target="_blank">Human Proteostasis Network Annotation website</a>.
</p>
<p>
The proteostasis network is a fundamental entity in biology with direct relevance to many diseases of protein conformation. 
However, it has not been well defined or annotated, which has hindered its functional characterization in health and disease. 
Here, we operationally define the human proteostasis network by providing a comprehensive, annotated list of its components.
</p>
<p>
To organize the proteostasis network components, we use a taxonomic scheme consisting of five levels: 
<b>Branch, Class, Group, Type, and Subtype</b>. We find that five levels are sufficient to convey a general sense of 
each component’s localization and function while minimizing the number of descriptors.
</p>
<div style="background-color: #F9FDFD; padding: 20px; border-radius: 8px; border: 1px solid #E0F7FA; margin: 20px 0;">
<p style="margin-bottom: 15px;">
<span class="term-highlight">Branch</span> refers to a component’s localization or membership in an overarching pathway. 
There are nine Branch categories: cytonuclear proteostasis (CY), ER proteostasis (ER), mitochondrial proteostasis (MI), 
nuclear proteostasis (NU), PN regulation (PN), translation (TR), extracellular proteostasis (EX), 
the autophagy-lysosome pathway (ALP), and the ubiquitin-proteasome system (UPS).
</p>
<p style="margin-bottom: 15px;">
<span class="term-highlight">Class</span> refers to a component’s function in proteostasis (e.g., chaperones, protein transport, etc.) 
in most Branches of the PN. In the ALP it refers to the stage of autophagy in which the component participates.
</p>
<p style="margin-bottom: 0px;">
<span class="term-highlight">Group, Type, and Subtype</span> provide increasingly specific descriptors of proteostasis functions within a Class.
</p>
</div>
<p>
Our goal was to use only as many descriptors as are minimally necessary to give a basic understanding of a component’s role in proteostasis. 
Thus, not every component has Type or Subtype annotations. Also, some components have multiple roles in the proteostasis network. 
These are given multiple entries in our list to reflect each separate role.
</p>

<div class="about-header">Indexing values for this catalog</div>
<p>
Individual entries in the <b>MAIN</b> tab are indexed by <span class="red-highlight">Gene ID</span>, 
<span class="red-highlight">Uniprot ID</span>, and official <span class="red-highlight">Gene Symbol</span>. 
<span class="red-highlight">Gene Synonyms</span> are additionally listed.
RNA genes are given arbitrary but unique designations in the <b>Uniprot ID</b> field to assist with data analysis.
Entries in the <b>UNIQUE</b> tab also include ENSG and HGNC designations.
</p>
<p>
The core <b>Proteostasis Network Annotation</b> can be found in the 
<span class="red-highlight">Branch, Class, Group, Type</span>, and <span class="red-highlight">Subtype</span> designations. 
Explanatory details about the fine structure of the annotation will be published in a forthcoming paper.
</p>
<div class="about-header">Branch-specific notes</div>
<ul class="about-list">
<li><b>“Cytonuclear”</b> refers to components that support proteostasis in both the cytosol and the nucleus.</li>
<li><b>“Nuclear”</b> refers to components that primarily support nuclear proteostasis (e.g., histone chaperones).</li>
<li><b>“Proteostasis regulation”</b> refers to components that control transcription or translation of proteostasis network components.</li>
<li>For the <b>ALP Branch</b>, Class annotations are based on the temporal progression of autophagy; see the Tallies tab for a terse list. Each component in the ALP Branch has a note explaining why it was included (see Notes column).</li>
<li>For the <b>UPS Branch</b>, annotations rely heavily on shared or characteristic Interpro domains, and these will be described in detail in the forthcoming paper.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    #st.markdown("<br><br><hr>", unsafe_allow_html=True)
    #st.caption("Data source: Human Proteostasis Network v4.3")

# ==========================================
# PAGE 4: GUIDES - REVISED HIERARCHY
# ==========================================
elif selected_page == "Guides":
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">User Guides</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Navigating the Human Proteostasis Network Annotation</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # HTML Block
    st.markdown("""
<style>
.guide-container {
    max-width: 900px;
    margin: 0 auto;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 16px;
    line-height: 1.6;
    color: #212121;
    padding-bottom: 50px;
}
.guide-header {
    font-size: 22px;
    font-weight: bold;
    color: #006064;
    margin-top: 40px;
    margin-bottom: 15px;
    border-bottom: 2px solid #E0F7FA;
    padding-bottom: 5px;
}
.guide-subheader {
    font-size: 18px;
    font-weight: bold;
    color: #00838F;
    margin-top: 20px;
    margin-bottom: 10px;
}
.term-highlight {
    font-weight: bold;
    color: #00838F;
    background-color: #E0F7FA;
    padding: 2px 6px;
    border-radius: 4px;
}
.code-highlight {
    font-family: monospace;
    background-color: #F0F0F0;
    padding: 2px 4px;
    border-radius: 4px;
    color: #B71C1C;
}
.guide-list {
    padding-left: 0px; 
    margin-left: 0px;
    list-style-type: none; 
    margin-bottom: 15px;
}
.guide-list li {
    margin-bottom: 12px;
}
.step-box {
    background-color: #FAFAFA;
    border-left: 4px solid #4DD0E1;
    padding: 15px;
    margin: 15px 0;
    border-radius: 0 4px 4px 0;
}
</style>

<div class="guide-container">
<p>
This application provides an interactive interface to the Human Proteostasis Network. 
Below are specific instructions on how the search engine processes your queries and how the results are annotated.
</p>

<div class="guide-header">1. Open Search Rules</div>

<div class="guide-subheader">Partial vs. Exact Matching</div>
<ul class="guide-list">
<li>
The search is case-insensitive. 
</li>
<li>
<b>Gene Symbols & Synonyms (Partial):</b> These allow partial matches. Searching for <span class="term-highlight">HSP</span> will return <i>HSPA1A</i>, <i>HSPB1</i>, and any gene containing those letters.
</li>
<li>
<b>Functional Terms & IDs (Exact):</b> Terms like <span class="term-highlight">Branch</span>, <span class="term-highlight">Class</span>, or <span class="term-highlight">UniProt ID</span> require an exact match. 
</li>
</ul>

<div class="step-box">
<b>Forced Exact Match:</b> If you want to find <i>only</i> a specific gene symbol and ignore all other partial hits, wrap your query in single quotes: <span class="code-highlight">'HSPA1A'</span>.
</div>

<div class="guide-subheader">Chemical Probes</div>
<ul class="guide-list">
<li>
<b>Chemical Probes Column:</b> Targets with validated small-molecule probes feature a clickable entry in the <span class="term-highlight">Chemical Probes</span> column at the far right.
</li>
<li>
<b>Hyperlinks:</b> Clicking the probe name (e.g., <i>rapamycin</i>) opens its full profile on the Chemical Probes Portal for detailed potency data.
</li>
<li>
<b>Multiple Entries:</b> If a target has several probes, they are listed and separated by a semicolon (;).
</li>
</ul>

<div class="guide-header">2. Using Guided Search</div>
<p>
The <b>Guided Search</b> page allows you to drill down into the network taxonomy. The filters are hierarchical; 
selecting an option in the first box updates the available options in the subsequent boxes.
</p>

<div class="guide-subheader">The Hierarchy Levels</div>
<ul class="guide-list">
<li><b>Branch:</b> Overarching pathway or localization (e.g., UPS, ALP).</li>
<li><b>Class:</b> Functional role within that branch (e.g., chaperone, protein transport).</li>
<li><b>Group/Type/Subtype:</b> Increasingly specific functional descriptors.</li>
</ul>

<div class="guide-header">3. Exporting Data</div>
<p>
You can export your results at any time:
</p>
<ul class="guide-list">
<li>1. Perform your search or apply your filters.</li>
<li>2. Click the <b>"Download CSV"</b> button located above the results table.</li>
<li>3. The file will save with your query name for easy reference.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    #st.markdown("<br><hr>", unsafe_allow_html=True)
    #st.caption("Data source: Human Proteostasis Network v4.3")

# ==========================================
# PAGE 5: SUBMISSION
# ==========================================
elif selected_page == "Submission":
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Submitting new Information to Human PN</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Introductory text matching the mockup style
    st.markdown("""
        <div style="max-width: 800px; margin: 0 auto 20px auto; font-family: Arial, Helvetica, sans-serif; font-size: 16px; color: #445550; background-color: #F0FBFC; padding: 20px; border-radius: 8px; border: 1px solid #E0F7FA;">
            New components involved in the human PN are welcome. To this end, fill in the form below with a brief summary of the new component information and evidence. After curating that information, we will add the new information to our annotation.
        </div>
    """, unsafe_allow_html=True)

    # Form Container
    with st.container():
        # Center the form using columns
        _, col_form, _ = st.columns([1, 4, 1])
        
        with col_form:
            with st.form("protein_submission_form", border=True):
                
                # Top row inputs
                c1, c2 = st.columns(2)
                with c1:
                    protein_name = st.text_input("Gene Symbol *", placeholder="Ex: HSPA1A")
                with c2:
                    # Adapted Organism Type from the mockup to UniProt ID for the PN context
                    uniprot_id = st.text_input("UniProt ID *", placeholder="Ex: P0DMV8")

                # Text areas
                description = st.text_area(
                    "Protein Description *", 
                    placeholder="Briefly describe the protein, its function in the proteostasis network",
                    help="Include relevant information about the function and characteristics of the protein."
                )
                
                evidence = st.text_area(
                    "Evidence *", 
                    placeholder="Provide scientific evidence, references or publications",
                    help="Include references to publications, experiments or annotations that support the information."
                )
                
                st.markdown("<hr style='border: 1px solid #F0F0F0; margin: 15px 0;'>", unsafe_allow_html=True)
                
                # Contact info
                st.markdown("<p style='font-family: Arial; font-size: 16px; font-weight: bold; color: #212121;'>Contact Information (optional)</p>", unsafe_allow_html=True)
                
                c3, c4 = st.columns(2)
                with c3:
                    contact_name = st.text_input("Name", placeholder="Your name")
                with c4:
                    contact_email = st.text_input("Email", placeholder="your.email@example.com")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # The submit button inside a form automatically prevents page reloads until clicked
                submit_button = st.form_submit_button("Submit Information", use_container_width=True)
                
                # Basic validation logic
                if submit_button:
                    if not protein_name or not uniprot_id or not description or not evidence:
                        st.error("Please fill in all the required fields marked with an asterisk (*).")
                    else:
                        st.success(f"Thank you! The information for {protein_name} has been submitted for curation.")
                        st.balloons() # Optional: A little celebration animation upon success