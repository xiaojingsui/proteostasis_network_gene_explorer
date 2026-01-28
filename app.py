import streamlit as st
import pandas as pd
import io

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state variables
if "search_key" not in st.session_state:
    st.session_state.search_key = ""
if "page" not in st.session_state:
    st.session_state.page = "Search"  # Default page

# CALLBACK FUNCTIONS
def update_search(new_query):
    st.session_state.search_key = new_query

def set_page(page_name):
    st.session_state.page = page_name

# 2. Custom CSS
st.markdown("""
    <style>
    /* GLOBAL FONTS */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #FBFEFF;
    }

    /* HIDE STANDARD STREAMLIT ELEMENTS */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; } /* Hides the top decoration bar */

    /* =========================================
       CUSTOM NAVIGATION BAR STYLING 
       ========================================= */
    
    /* 1. Style the Primary Button (Active Page) to look like a 'Blue Pill' */
    div.stButton > button[kind="primary"] {
        background-color: #E3F2FD !important; /* Light Blue Background */
        color: #1565C0 !important;           /* Dark Blue Text */
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        padding: 0px 20px !important;
        height: 38px !important;
        box-shadow: none !important;
    }

    /* 2. Style the Secondary Button (Inactive Page) to look like plain text */
    div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #555555 !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0px 20px !important;
        height: 38px !important;
        box-shadow: none !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        color: #1565C0 !important;
        background-color: #F5F5F5 !important;
        border-radius: 20px !important;
    }

    /* 3. Navbar Container Styling */
    .navbar-container {
        display: flex;
        align-items: center;
        padding-bottom: 10px;
        border-bottom: 1px solid #E0E0E0;
        margin-bottom: 20px;
    }

    /* LOGO STYLING */
    .nav-logo-title {
        font-size: 20px;
        font-weight: 800;
        color: #263238;
        margin: 0;
        line-height: 1.2;
    }
    .nav-logo-subtitle {
        font-size: 12px;
        color: #78909C;
        margin: 0;
    }

    /* =========================================
       DATA TABLE STYLING 
       ========================================= */
    td { 
        font-family: Arial, Helvetica, sans-serif !important;
        padding: 15px !important; 
        border-bottom: 1px solid #F0F0F0 !important; 
        font-size: 14px !important; 
        color: #212121 !important; 
        background-color: #FFFFFF !important; 
    }
    th { 
        font-family: Arial, Helvetica, sans-serif !important;
        background-color: #F0FBFC !important; 
        color: #006064 !important; 
        text-align: left !important; 
        padding: 15px !important; 
    }
    .result-container {
        width: 100%;
        border-collapse: collapse;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* GENERAL UI ELEMENTS */
    h4 { color: #333; font-weight: 700; }
    a { color: #00838F !important; text-decoration: none; font-weight: bold; }
    
    .hero-title {
        font-size: 42px; font-weight: 800; color: #000; margin-bottom: 10px; text-align: center;
    }
    .hero-subtitle {
        font-size: 20px; color: #006064; margin-bottom: 30px; text-align: center;
    }
    
    /* Input Field Styling */
    div[data-testid="stTextInput"] { width: 60%; margin: 0 auto; }
    div[data-testid="stTextInput"] input {
        border-radius: 25px !important;
        border: 2px solid #4DD0E1 !important;
        padding: 15px 25px !important;
    }
    
    .info-box {
        background-color: white; border: 1px solid #B2EBF2; border-left: 5px solid #00838F;
        padding: 20px; border-radius: 5px; height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    file_path = 'Human Proteostasis Network 4.1 - 2026-0127.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='MAIN')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        # st.error(f"Error loading file: {e}") # Suppress error for demo if file missing
        return pd.DataFrame() # Return empty for now

df = load_data()

# ==========================================
# CUSTOM TOP NAVIGATION BAR
# ==========================================
def render_navbar():
    # Use columns to create the layout: [Logo | Nav Items | External Link]
    # Adjust ratios: Logo(2.5) | Gap(3) | Search(1) | About(1) | Gap(1.5) | ExtLink(2)
    
    # Creates a container with a white background feel
    with st.container():
        c_logo, _, c_nav1, c_nav2, _, c_link = st.columns([2.5, 3, 0.8, 0.8, 1.5, 1.5])
        
        # 1. Logo Section
        with c_logo:
            st.markdown("""
                <div style="display:flex; align-items:center; height: 100%;">
                    <div style="background-color:#E0F7FA; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-right:10px;">
                        <span style="font-size:20px;">🧬</span>
                    </div>
                    <div>
                        <p class="nav-logo-title">Human PN DB</p>
                        <p class="nav-logo-subtitle">Proteostasis Network</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # 2. Navigation Buttons (Search & About)
        # logic: If active page is 'Search', button type is 'primary' (blue pill), else 'secondary' (text)
        with c_nav1:
            if st.button("Search", key="nav_search", type="primary" if st.session_state.page == "Search" else "secondary"):
                set_page("Search")
                st.rerun()
                
        with c_nav2:
            if st.button("About", key="nav_about", type="primary" if st.session_state.page == "About" else "secondary"):
                set_page("About")
                st.rerun()

        # 3. External Link
        with c_link:
            st.markdown("""
            <div style="text-align: right; padding-top: 5px;">
                <a href="https://github.com/" target="_blank" style="color:#555 !important; font-weight:normal;">
                   ↗ Laboratory
                </a>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<hr style='margin: 0px 0px 30px 0px; border-color: #F0F0F0;'>", unsafe_allow_html=True)

# ==========================================
# PAGE CONTENT: SEARCH
# ==========================================
def show_search_page():
    st.markdown('<p class="hero-title">HUMAN Proteostasis Network</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

    # Search Bar
    query = st.text_input("", placeholder="Search Gene, ID, or Function...", value=st.session_state.search_key)
    if query != st.session_state.search_key:
        st.session_state.search_key = query
        # No rerun needed here usually, but if you want instant updates:
        # st.rerun()

    # Quick Search Chips
    st.markdown('<div style="margin-top: 15px; text-align: center;">', unsafe_allow_html=True)
    col_chip_L, c1, c2, c3, col_chip_R = st.columns([3, 1, 1, 1, 3])
    
    def chip_click(label):
        st.session_state.search_key = label
        st.rerun()

    with c1: st.button("HSPA1A", on_click=chip_click, args=("HSPA1A",))
    with c2: st.button("P0DMV8", on_click=chip_click, args=("P0DMV8",))
    with c3: st.button("Chaperone", on_click=chip_click, args=("Chaperone",))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Results
    if st.session_state.search_key:
        q = st.session_state.search_key
        # Filter Logic
        mask = df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)
        results = df[mask].copy()

        if not results.empty:
            c_res, c_down = st.columns([6, 1])
            with c_res: st.markdown(f"#### Found {len(results)} matches")
            with c_down:
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="results.csv", mime="text/csv")
            
            # Formatting Links
            results['UniProt ID'] = results['UniProt ID'].apply(lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>')
            
            cols = ['UniProt ID', 'Gene Symbol', 'Branch', 'Class', 'Group', 'Type'] # Adjust based on your actual columns
            avail_cols = [c for c in cols if c in results.columns]
            
            st.write(results[avail_cols].to_html(escape=False, index=False, classes='result-container'), unsafe_allow_html=True)
        else:
            st.info(f"No results found for '{q}'")

# ==========================================
# PAGE CONTENT: ABOUT
# ==========================================
def show_about_page():
    st.markdown("## About the Project")
    st.markdown("This database provides a comprehensive enumeration of the Human Proteostasis Network.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="info-box"><strong>Contact Information</strong><br><br>Evan Powers<br>Suzanne Elsasser<br>Xiaojing Sui</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-box"><strong>Citation</strong><br><br>Please cite: <em>A Comprehensive Enumeration of the Human Proteostasis Network (2022)</em>.</div>', unsafe_allow_html=True)

# ==========================================
# MAIN APP EXECUTION
# ==========================================

# 1. Render the Top Navbar (Always visible)
render_navbar()

# 2. Render the specific page content
if st.session_state.page == "Search":
    show_search_page()
elif st.session_state.page == "About":
    show_about_page()