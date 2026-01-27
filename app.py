import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Human PN Database", layout="wide")

# Initialize session state for the key
if "search_key" not in st.session_state:
    st.session_state.search_key = ""

# 2. Custom CSS (Global + Tabs + Top Search)
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    
    /* Top Header Styling */
    .top-header {
        color: #00838F;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 5px;
    }
    .top-sub {
        color: #006064;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Input Styling - Moved to Top */
    div[data-testid="stTextInput"] {
        width: 100% !important; 
    }
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 8px !important;
        padding: 15px 20px !important;
        font-size: 18px !important; 
        border: 1px solid #B2EBF2 !important;
        border-bottom: 3px solid #4DD0E1 !important;
        background-color: white !important;
    }
    
    /* Customizing Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        justify-content: flex-start; /* Align tabs to left or center */
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px;
        color: #006064;
        font-size: 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #00838F !important;
        border-bottom: 3px solid #00838F;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Table Styling */
    .result-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        width: 100%;
        margin-top: 10px;
        border-collapse: collapse;
    }
    th { background-color: #F0FBFC !important; color: #006064 !important; text-align: left !important; padding: 12px !important; }
    td { padding: 12px !important; border-bottom: 1px solid #F0F0F0 !important; font-size: 14px; }
    
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
        df = pd.read_excel(file_path, sheet_name='Proteostasis_Network_2024_0414')
        df = df.dropna(subset=['Gene Symbol', 'UniProt ID'])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data()

# 4. App Title (Compact)
st.markdown('<div class="top-header">HUMAN Proteostasis Network Database</div>', unsafe_allow_html=True)

# 5. Navigation Tabs
tab_search, tab_download = st.tabs(["🔍 Search Database", "📥 Download Data"])

# ==========================================
# TAB 1: SEARCH DATABASE
# ==========================================
with tab_search:
    # ---------------- SEARCH BAR (VERY TOP) ----------------
    def update_search(new_query):
        st.session_state.search_key = new_query

    # Using columns to center the search bar slightly, or keep it full width
    c_search, _ = st.columns([1, 0.01]) 
    with c_search:
        st.text_input(
            "", 
            placeholder="Type a Gene Symbol, UniProt ID, Domain (e.g., IPR001353), or Class...", 
            label_visibility="collapsed",
            key="search_key" 
        )

    # ---------------- SUGGESTION CHIPS ----------------
    # Placed immediately below search bar for quick access
    st.markdown('<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px; margin-top: -10px;">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([0.8, 0.5, 0.5, 4])
    with c1:
        st.caption("Try searching:")
    with c2:
        st.button("HSPA1A", on_click=update_search, args=("HSPA1A",), use_container_width=True)
    with c3:
        st.button("Chaperone", on_click=update_search, args=("Chaperone",), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- RESULTS LOGIC ----------------
    query = st.session_state.search_key
    if query:
        # Filter Logic
        mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        results = df[mask].copy()
        
        if not results.empty:
            st.success(f"Found {len(results)} matches for **'{query}'**")
            
            # --- 1. UniProt Link ---
            results['UniProt ID'] = results['UniProt ID'].apply(
                lambda x: f'<a href="https://www.uniprot.org/uniprotkb/{x}/entry" target="_blank">{x}</a>'
            )
            
            # --- 2. NCBI Gene Link ---
            if 'GeneID' in results.columns:
                def create_ncbi_link(val):
                    if pd.isna(val) or val == "": return ""
                    try:
                        clean_id = str(int(float(val))) 
                        return f'<a href="https://www.ncbi.nlm.nih.gov/gene/{clean_id}" target="_blank">{clean_id}</a>'
                    except:
                        return f'<a href="https://www.ncbi.nlm.nih.gov/gene/?term={val}" target="_blank">{val}</a>'
                results['GeneID'] = results['GeneID'].apply(create_ncbi_link)

            # --- 3. InterPro Domain Links ---
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
            
            # Display
            display_cols = [
                'UniProt ID', 'Gene Symbol', 'GeneID', 'Branch', 
                'Class', 'Group', 'Type', 'Subtype', 
                'Principal Domains', 'Auxiliary Domains'
            ]
            available_cols = [c for c in display_cols if c in results.columns]
            
            st.write(
                results[available_cols].to_html(escape=False, index=False, border=0, classes='result-container'), 
                unsafe_allow_html=True
            )
        else:
            st.warning(f"No results found for '{query}'. Try a different keyword.")
    else:
        # Empty State - Optional instructional text
        st.info("👆 Enter a gene symbol (e.g., DNAJB1) or ID above to start searching.")

# ==========================================
# TAB 2: DOWNLOAD DATA
# ==========================================
with tab_download:
    st.markdown("### 📥 Download Full Dataset")
    st.write("Access the original source file for your own analysis.")
    
    c_dl_1, c_dl_2 = st.columns([2, 1])
    
    with c_dl_1:
        st.dataframe(df.head(8), height=300)
        st.caption("Preview of the first 8 rows")
        
    with c_dl_2:
        st.write(" ")
        file_name = 'Human Proteostasis Network 2.0 ~ 2024-0415.xlsx'
        try:
            with open(file_name, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.error("Source file not found.")

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Data source: Human Proteostasis Network 2.0 ~ 2024-0415")