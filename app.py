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
    st.session_state.page = "Open Search"

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
        # Fill NaN in hierarchy columns with empty strings to avoid dropdown errors
        hierarchy_cols = ['Branch', 'Class', 'Group', 'Type', 'Subtype']
        for col in hierarchy_cols:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. HELPER FUNCTIONS FOR LINKS
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

    # Interpro Links
    if 'Interpro Domains' in df_copy.columns:
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
        df_copy['Interpro Domains'] = df_copy['Interpro Domains'].apply(create_interpro_links)
        
    return df_copy

# 4. GLOBAL CSS
st.markdown("""
    <style>
    /* --- GLOBAL FONTS & MAIN CONTAINER --- */
    /* Force Arial on everything in the app */
    html, body, [data-testid="stAppViewContainer"], .stApp, p, h1, h2, h3, h4, h5, h6, span, div {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FBFEFF;
        color: #212121 !important;
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

    /* --- WIDGET STYLING (Inputs & Selectboxes) --- */
    
    /* Text Inputs */
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

    div[data-testid="stTextInput"] input:focus {
    outline: none !important;     /* 1. Kills default browser line */
    box-shadow: none !important;  /* 2. Kills Streamlit red glow */
    border: 2px solid #4DD0E1 !important; /* Replaces it with your Teal border */
    }

    div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within {
    border: none !important;      /* Removes wrapper border */
    box-shadow: none !important;  /* Removes wrapper red glow */
    outline: none !important;
    }

    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Selectboxes (Dropdowns) - Force Arial on everything */
    div[data-testid="stSelectbox"] * {
        font-family: Arial, Helvetica, sans-serif !important;
    }
    
    /* Target the Label of the Selectbox specifically */
    div[data-testid="stSelectbox"] label p {
        font-size: 14px !important;
        color: #445550 !important;
    }

    /* Target the dropdown popover menu items */
    div[role="listbox"] * {
         font-family: Arial, Helvetica, sans-serif !important;
    }

    /* Style the main box of the selectbox */
    div[data-testid="stSelectbox"] > div > div {
        border-color: #4DD0E1 !important;
        border-width: 2px !important;
    }


    /* --- BUTTON STYLING (Force Light Theme) --- */
    
    /* 1. Normal State (Idle) - This forces the button to be white even in Dark Mode */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #212121 !important;             /* Dark text */
        border: 1px solid #D3D3D3 !important;  /* Light grey border */
        transition: all 0.3s ease !important;
    }

    /* 2. Hover State - Your custom teal styling */
    div.stButton > button:hover {
        background-color: #F0FBFC !important; /* Very light teal tint */
        color: #004D40 !important;            /* Darker Teal text */
        border-color: #006064 !important;     /* Darker border */
    }

    /* 3. Active/Focus State (When clicked) */
    div.stButton > button:active, div.stButton > button:focus {
        background-color: #FFFFFF !important;
        color: #006064 !important;
        border-color: #006064 !important;
        box-shadow: none !important;
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
NAV_OPTIONS = ["Open Search", "Guided Search", "About", "Guides"]

selected_nav = st.radio(
    "Navigation", 
    NAV_OPTIONS, 
    horizontal=True, 
    label_visibility="collapsed",
    key="nav_radio"
)

selected_page = selected_nav


# ==========================================
# PAGE 1: SEARCH (KEYWORD)
# ==========================================
if selected_page == "Open Search":

    df = load_data()

    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">HUMAN Proteostasis Network Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

    # Search Input
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

    # Results Logic
    query = st.session_state.search_key
    if query:
        if df.empty:
             st.error("Database could not be loaded. Please check the source file.")
        else:
            clean_query = query.strip().lower()

            # --- SEARCH STRATEGY DEFINITION ---
            exact_cols = ['Gene Symbol', 'Gene ID', 'UniProt ID', 'Branch', 'Class', 'Group', 'Type', 'Subtype']
            list_cols = ['Interpro Domains']

            # 1. Check Exact Columns
            valid_exact = [c for c in exact_cols if c in df.columns]
            mask_exact = pd.Series(False, index=df.index)
            if valid_exact:
                mask_exact = df[valid_exact].astype(str).apply(
                    lambda x: x.str.strip().str.lower() == clean_query
                ).any(axis=1)

            # 2. Check List Columns (Interpro)
            valid_list = [c for c in list_cols if c in df.columns]
            mask_list = pd.Series(False, index=df.index)
            
            if valid_list:
                def list_contains_exact(cell_val, q_val):
                    if pd.isna(cell_val): return False
                    items = [item.strip().lower() for item in str(cell_val).replace(';', ',').split(',')]
                    return q_val in items

                mask_list = df[valid_list].apply(
                    lambda col: col.apply(lambda cell: list_contains_exact(cell, clean_query))
                ).any(axis=1)

            # 3. Combine Results
            final_mask = mask_exact | mask_list
            results = df[final_mask].copy()
            
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
                
                # Use Helper to format links
                results = format_links(results)
                
                display_cols = ['UniProt ID', 'Gene ID', 'Gene Symbol','Gene Synonyms', 'Branch', 'Class', 'Group', 'Type', 'Subtype', 'Interpro Domains']
                available_cols = [c for c in display_cols if c in results.columns]
                
                st.write(
                    results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                    unsafe_allow_html=True
                )
            else:
                
                # REVISED NO RESULTS NOTIFICATION (White Background, Smaller, Centered)
                st.markdown(f"""
                    <div style="
                        background-color: #FFFFFF;
                        padding: 20px;
                        border-radius: 8px;
                        color: #E65100;
                        border: 1px solid #FFE082;
                        text-align: center;
                        margin: 20px auto; 
                        width: 33%;
                        min-width: 300px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    ">
                        <span style="font-size: 16px; font-weight: bold;">No results found for '{query}'</span><br>
                        <span style="font-size: 14px; color: #8D6E63;">Please try a different query term.</span>
                    </div>
                """, unsafe_allow_html=True)

    # Footer Logic (Same as before)
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
                <p style="margin-bottom: 0; font-size: 0.9em;">
                    2. A Comprehensive Enumeration of the Human Proteostasis Network. 2. Components of the Autophagy-Lysosome Pathway 
                    <a href="https://doi.org/10.1101/2023.03.22.533675" target="_blank">doi:10.1101/2023.03.22.533675</a>
                </p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")


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
            # REMOVED sorted() to preserve Excel order
            branches = df['Branch'].unique().tolist()
            branches = [x for x in branches if x] 
            sel_branch = c1.selectbox("1. Select Branch", [""] + branches)

            # Logic: Filter DF based on Branch
            df_lvl1 = df[df['Branch'] == sel_branch] if sel_branch else df

            # 2. Class Selection (Depends on Branch)
            if sel_branch:
                # REMOVED sorted()
                classes = df_lvl1['Class'].unique().tolist()
                classes = [x for x in classes if x] 
                sel_class = c2.selectbox("2. Select Class (Optional)", [""] + classes)
            else:
                sel_class = c2.selectbox("2. Select Class", [], disabled=True, placeholder="Select Branch first")

            # Logic: Filter DF based on Class
            df_lvl2 = df_lvl1[df_lvl1['Class'] == sel_class] if (sel_branch and sel_class) else df_lvl1

            # 3. Group Selection (Depends on Class)
            if sel_branch and sel_class:
                # REMOVED sorted()
                groups = df_lvl2['Group'].unique().tolist()
                groups = [x for x in groups if x]
                sel_group = c3.selectbox("3. Select Group (Optional)", [""] + groups)
            else:
                sel_group = c3.selectbox("3. Select Group", [], disabled=True, placeholder="Select Class first")

            # Logic: Filter DF based on Group
            df_lvl3 = df_lvl2[df_lvl2['Group'] == sel_group] if (sel_branch and sel_class and sel_group) else df_lvl2

            # Row 2: Type, Subtype
            c4, c5 = st.columns(2)

            # 4. Type Selection (Depends on Group)
            if sel_branch and sel_class and sel_group:
                # REMOVED sorted()
                types = df_lvl3['Type'].unique().tolist()
                types = [x for x in types if x]
                sel_type = c4.selectbox("4. Select Type (Optional)", [""] + types)
            else:
                sel_type = c4.selectbox("4. Select Type", [], disabled=True, placeholder="Select Group first")

            # Logic: Filter DF based on Type
            df_lvl4 = df_lvl3[df_lvl3['Type'] == sel_type] if (sel_branch and sel_class and sel_group and sel_type) else df_lvl3

            # 5. Subtype Selection (Depends on Type)
            if sel_branch and sel_class and sel_group and sel_type:
                # REMOVED sorted()
                subtypes = df_lvl4['Subtype'].unique().tolist()
                subtypes = [x for x in subtypes if x]
                sel_subtype = c5.selectbox("5. Select Subtype (Optional)", [""] + subtypes)
            else:
                sel_subtype = c5.selectbox("5. Select Subtype", [], disabled=True, placeholder="Select Type first")
            
            # Final Filter Logic
            final_df = df_lvl4[df_lvl4['Subtype'] == sel_subtype] if (sel_branch and sel_class and sel_group and sel_type and sel_subtype) else df_lvl4

        # --- DISPLAY RESULTS ---
        st.divider()
        
        if sel_branch:
            col_res_header, col_res_dl = st.columns([7, 1])
            with col_res_header:
                st.markdown(f"#### Found {len(final_df)} entries")
                breadcrumb = f"{sel_branch}"
                if sel_class: breadcrumb += f" > {sel_class}"
                if sel_group: breadcrumb += f" > {sel_group}"
                if sel_type: breadcrumb += f" > {sel_type}"
                if sel_subtype: breadcrumb += f" > {sel_subtype}"
                st.caption(f"Filter: {breadcrumb}")

            with col_res_dl:
                st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
                display_cols = ['UniProt ID', 'Gene ID', 'Gene Symbol', 'Gene Synonyms','Branch', 'Class', 'Group', 'Type', 'Subtype', 'Interpro Domains']
                valid_cols = [c for c in display_cols if c in final_df.columns]
                csv = final_df[valid_cols].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="guided_search_results.csv",
                    mime="text/csv",
                )

            # Apply Link Formatting
            display_df = format_links(final_df)
            available_cols = [c for c in display_cols if c in display_df.columns]
            
            st.write(
                display_df[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                unsafe_allow_html=True
            )
        else:
            # Styled info box to match Arial theme
            st.markdown("""
                <div style="background-color: #E1F5FE; padding: 15px; border-radius: 8px; color: #0277BD; border: 1px solid #B3E5FC;">
                    Please select a <b>Branch</b> to begin the guided search.
                </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")


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

    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")

# ==========================================
# ==========================================
# PAGE 4: GUIDES
# ==========================================
elif selected_page == "Guides":
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">User Guides</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Navigating the Human Proteostasis Network Database</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # HTML Block - Content is flushed left to match your screenshot structure
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
.guide-list {
padding-left: 20px;
margin-bottom: 15px;
}
.guide-list li {
margin-bottom: 10px;
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
Below are detailed instructions on how to utilize the search functions and interpret the data hierarchy.
</p>

<div class="guide-header">1. Using Open Search</div>
<p>
The <b>Open Search</b> page is designed for quick retrieval of specific genes or broad exploration of functional terms.
</p>

<div class="guide-subheader">Search Logic</div>
<ul class="guide-list">
<li>
<b>Identifiers:</b> You can search directly by <span class="term-highlight">Gene Symbol</span> (e.g., <i>HSPA1A</i>) or <span class="term-highlight">UniProt ID</span> (e.g., <i>P0DMV8</i>).
</li>
<li>
<b>Keywords:</b> You can search for functional terms found in the hierarchy, such as "Chaperone", "Translation", or "PN regulation", etc.
</li>
<li>
<b>InterPro Domains:</b> The engine searches within the domain lists. You can search for specific domain IDs (e.g., <i>IPR001234</i>).
</li>
<li>
<b>Exact vs. Partial:</b> The search is case-insensitive. For Gene Symbols, IDs and functional terms, it prioritizes exact matches, but will also scan lists (like domains) for the presence of your query.
</li>
</ul>

<div class="step-box">
<b>Tip:</b> If you would like to explore based on PN function, try switching to <b>Guided Search</b> to filter.
</div>

<div class="guide-header">2. Using Guided Search</div>
<p>
The <b>Guided Search</b> page allows you to drill down into the network taxonomy. The filters are hierarchical; 
selecting an option in the first box updates the available options in the subsequent boxes.
</p>

<div class="guide-subheader">The Hierarchy Levels</div>

<ul class="guide-list">
<li><b> Branch:</b> Refers to a component’s localization or membership in an overarching pathway. There are nine Branch categories: cytonuclear proteostasis, ER proteostasis, mitochondrial proteostasis, nuclear proteostasis, PN regulation, translation, extracellular proteostasis, the autophagy-lysosome pathway, and the ubiquitin-proteasome system.</li>
<li><b> Class:</b> Refers to a component’s function in proteostasis (e.g., chaperones, protein transport, etc.) in most Branches of the PN. In the ALP it refers to the stage of autophagy in which the component participates.</li>
<li><b> Group:</b> Provide increasingly specific descriptors of proteostasis functions within a Class.</li>
<li><b> Type:</b> Provide increasingly specific descriptors of proteostasis functions within a Group.</li>
<li><b> Subtype:</b> Provide increasingly specific descriptors of proteostasis functions within a Type.</li>
</ul>

<div class="step-box">
<b>Note:</b> Not all genes have data for Type or Subtype. These dropdowns are marked "Optional" and may remain empty for certain branches.
</div>

<div class="guide-header">3. Interpreting Results & External Links</div>
<p>
Both search modes generate a standard results table containing the following interactive features:
</p>
<ul class="guide-list">
<li>
<span class="term-highlight">UniProt ID</span>: Clicking this value opens the official UniProtKB entry in a new tab.
</li>
<li>
<span class="term-highlight">Gene ID</span>: Clicking this value opens the NCBI Gene database entry.
</li>
<li>
<span class="term-highlight">InterPro Domains</span>: Specific domains listed (starting with IPR) are hyperlinked to the EBI InterPro database for structural analysis.
</li>
</ul>

<div class="guide-header">4. Exporting Data</div>
<p>
You can export the results of any search (Open or Guided) for offline analysis.
</p>
<ol class="guide-list">
<li>Perform your search or apply your filters.</li>
<li>Locate the <b>"Download CSV"</b> button in the top right corner of the results area.</li>
<li>The file will save automatically with a relevant filename (e.g., <i>search_results_HSPA1A.csv</i>).</li>
</ol>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("Data source: Human Proteostasis Network v4.1")