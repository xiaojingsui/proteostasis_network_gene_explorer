import streamlit as st
import pandas as pd
import io
import textwrap

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
        # Load data (adjust sheet name if necessary)
        df = pd.read_excel(file_path, sheet_name='MAIN')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        # Fill NaN values in hierarchy columns with empty strings for smoother filtering
        fill_cols = ['Branch', 'Class', 'Group', 'Type', 'Subtype']
        for c in fill_cols:
            if c in df.columns:
                df[c] = df[c].fillna("N/A")
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

    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    div[role="radiogroup"] label {
        margin-right: 0px !important;
    }

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

    /* --- INPUT & SELECT BOX STYLING --- */
    
    /* Target the main Text Input (Global width rule) */
    div[data-testid="stTextInput"] {
        width: 50% !important;
        min-width: 300px;
        margin: 0 auto -15px !important;
    }

    div[data-testid="stTextInput"] > div {
        height: auto !important;
        min-height: 75px !important; 
    }

    div[data-testid="stTextInput"] > div > div > input {
        font-family: Arial, Helvetica, sans-serif !important;
        border-radius: 12px !important;
        box-sizing: border-box !important; 
        padding: 22px 25px !important;
        font-size: 15px !important;
        border: 2px solid #4DD0E1 !important; 
        background-color: white !important;
        color: #006064 !important; 
    }

    /* Specific Styling for Selectboxes (Dropdowns) to match theme */
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1px solid #4DD0E1 !important;
        background-color: #FFFFFF !important;
        color: #006064 !important;
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
    
    /* Advanced Search Specifics - Restore width for dropdowns inside columns */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stTextInput"] {
        width: 100% !important; /* Overrides the global 50% rule for inputs inside columns if needed */
        margin: 0 !important;
    }
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
NAV_OPTIONS = ["🔍 Search", "⚡ Advanced Search", "ℹ️ About"]

selected_nav = st.radio(
    "Navigation", 
    NAV_OPTIONS, 
    horizontal=True, 
    label_visibility="collapsed",
    key="nav_radio"
)

# Page Router
if "Search" in selected_nav and "Advanced" not in selected_nav:
    selected_page = "Search"
elif "Advanced" in selected_nav:
    selected_page = "Advanced"
else:
    selected_page = "About"


# ==========================================
# PAGE 1: SEARCH (MAIN)
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

                    display_cols = [
                        'UniProt ID', 'Gene ID', 'Gene Symbol', 'Branch', 
                        'Class', 'Group', 'Type', 'Subtype', 
                        'Interpro Domains'
                    ]
                    valid_cols = [c for c in display_cols if c in results.columns]
                    csv = results[valid_cols].to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"search_results_{query}.csv",
                        mime="text/csv",
                    )
                
                # Link Formatting (Helper functions)
                results['UniProt ID'] = results['UniProt ID'].apply(
                    lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
                )
                
                if 'Gene ID' in results.columns:
                    def create_ncbi_link(val):
                        if pd.isna(val) or str(val) == "": return ""
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

    # Footer
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")


# ==========================================
# PAGE 2: ADVANCED SEARCH
# ==========================================
elif selected_page == "Advanced":
    
    df = load_data()

    # Hero Section Small
    st.markdown('<div class="hero-section" style="padding-bottom: 10px;">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title" style="font-size: 36px;">Advanced Catalog Search</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle" style="font-size: 18px;">Filter by hierarchy. Options update based on selection.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if df.empty:
        st.error("Data could not be loaded.")
    else:
        # Container for filters
        with st.container():
            st.markdown("""
                <style>
                /* Override the 50% width rule specifically for this page's selectboxes/inputs */
                div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"] > div {
                    width: 100% !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # CASCADING FILTERS
            # We create a progressive filtering object. 
            # Note: We filter a COPY of the dataframe for display, but we calculate options based on the progressive state.

            filtered_df = df.copy()

            # Row 1: Branch & Class
            col1, col2 = st.columns(2)
            
            with col1:
                # Branch options are always all branches
                branch_opts = sorted(df['Branch'].unique().astype(str).tolist())
                sel_branch = st.selectbox("Branch", ["All"] + branch_opts)
                
                if sel_branch != "All":
                    filtered_df = filtered_df[filtered_df['Branch'] == sel_branch]

            with col2:
                # Class options depend on Branch selection
                class_opts = sorted(filtered_df['Class'].unique().astype(str).tolist())
                sel_class = st.selectbox("Class", ["All"] + class_opts)
                
                if sel_class != "All":
                    filtered_df = filtered_df[filtered_df['Class'] == sel_class]

            # Row 2: Group & Type
            col3, col4 = st.columns(2)
            
            with col3:
                # Group options depend on Branch + Class
                group_opts = sorted(filtered_df['Group'].unique().astype(str).tolist())
                sel_group = st.selectbox("Group", ["All"] + group_opts)
                
                if sel_group != "All":
                    filtered_df = filtered_df[filtered_df['Group'] == sel_group]

            with col4:
                # Type options depend on previous
                type_opts = sorted(filtered_df['Type'].unique().astype(str).tolist())
                sel_type = st.selectbox("Type", ["All"] + type_opts)
                
                if sel_type != "All":
                    filtered_df = filtered_df[filtered_df['Type'] == sel_type]

            # Row 3: Subtype & Text Filter
            col5, col6 = st.columns(2)
            
            with col5:
                 # Subtype options depend on previous
                subtype_opts = sorted(filtered_df['Subtype'].unique().astype(str).tolist())
                sel_subtype = st.selectbox("Subtype", ["All"] + subtype_opts)
                
                if sel_subtype != "All":
                    filtered_df = filtered_df[filtered_df['Subtype'] == sel_subtype]
            
            with col6:
                # Optional Text refinement
                # We need to use a custom key to avoid conflict with main page
                text_filter = st.text_input("Refine by Gene Symbol (contains)", key="adv_text_filter")
                if text_filter:
                    filtered_df = filtered_df[filtered_df['Gene Symbol'].astype(str).str.contains(text_filter, case=False, na=False)]


        # --- DISPLAY RESULTS ---
        st.markdown("---")
        
        # Determine if we should show results (default to showing all if nothing selected, or handle heavy load)
        # Showing all 5000+ rows might be heavy, but let's assume it's okay for <10k rows.
        
        results_count = len(filtered_df)
        
        c_res, c_down = st.columns([8, 2])
        with c_res:
            st.markdown(f"**Found {results_count} entries**")
        
        with c_down:
             # CSV Export Logic
             display_cols = ['UniProt ID', 'Gene ID', 'Gene Symbol', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 'Interpro Domains']
             valid_cols = [c for c in display_cols if c in filtered_df.columns]
             csv_adv = filtered_df[valid_cols].to_csv(index=False).encode('utf-8')
             st.download_button(
                 label="Download Filtered CSV",
                 data=csv_adv,
                 file_name="advanced_search_results.csv",
                 mime="text/csv"
             )

        # Apply Link Formatting (Same as Main Page)
        # Note: We work on a .copy() for display to not break the next rerun logic
        display_df = filtered_df.copy()
        
        # Link Logic (Duplicated for isolation)
        display_df['UniProt ID'] = display_df['UniProt ID'].apply(
            lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
        )
        if 'Gene ID' in display_df.columns:
            display_df['Gene ID'] = display_df['Gene ID'].apply(
                lambda val: f'<a href="https://www.ncbi.nlm.nih.gov/gene/{int(float(val))}" target="_blank">{int(float(val))}</a>' if (pd.notna(val) and str(val)!="") else ""
            )
        
        # Just reuse the display columns logic
        valid_display = [c for c in display_cols if c in display_df.columns]
        
        st.write(
            display_df[valid_display].to_html(escape=False, index=False, border=0, classes='result-container'), 
            unsafe_allow_html=True
        )


# ==========================================
# PAGE 3: ABOUT
# ==========================================
elif selected_page == "About":
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">About the Project</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # MAIN CONTENT START
    st.markdown("""
    <style>
    .about-container {
        max-width: 900px;
        margin: 0 auto;
        font-family: Arial, Helvetica, sans-serif;
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
        
        <div class="about-header">How to use this interface</div>
        <p>The interface is open for immediate use and allows you to:</p>
        <ul class="about-list">
            <li>
                <span class="term-highlight">Search flexibly:</span> Query by <b>Gene Symbol</b> (e.g., HSPA1A), <b>UniProt ID</b>, or functional keywords (e.g., “Chaperone”), with direct links to UniProt, NCBI, and InterPro databases.
            </li>
            <li>
                <span class="term-highlight">Advanced Search:</span> Use the catalog view to filter hierarchically by Branch, Class, Group, Type, and Subtype.
            </li>
            <li>
                <span class="term-highlight">Export Data:</span> Use the <b>“Download CSV”</b> button to export your search results for offline analysis.
            </li>
        </ul>

        <div class="about-header">Indexing values for this catalog</div>
        <p>
            Individual entries in the <b>MAIN</b> tab are indexed by <span class="red-highlight">Gene ID</span>, 
            <span class="red-highlight">Uniprot ID</span>, and official <span class="red-highlight">Gene Symbol</span>. 
            <span class="red-highlight">Gene Synonyms</span> are additionally listed.
            RNA genes are given arbitrary but unique designations in the <b>Uniprot ID</b> field to assist with data analysis.
            Entries in the <b>UNIQUE</b> tab also include ENSG and HGNC designations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")