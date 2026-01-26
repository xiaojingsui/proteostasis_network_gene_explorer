import streamlit as st
import pandas as pd
import py3Dmol
from stmol import showmol
import requests

# 1. Page Config
st.set_page_config(page_title="PN Explorer", layout="wide")

# 2. Custom CSS for PhaSepDB Design
st.markdown("""
    <style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(180deg, #1a3a8a 0%, #2563eb 40%, #ffffff 100%);
    }
    /* Center the search section */
    .hero-section {
        padding: 60px 0px;
        text-align: center;
        color: white;
    }
    .hero-title {
        font-size: 64px !important;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 24px;
        opacity: 0.9;
        margin-bottom: 30px;
    }
    /* Style the text input to look like the image */
    div.stTextInput > div > div > input {
        border-radius: 10px;
        height: 50px;
        font-size: 18px;
    }
    /* Style info boxes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: none;
        color: #1e3a8a;
    }
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
    except:
        return pd.DataFrame()

df = load_data()

# 4. Hero Header (Centered Design)
st.markdown('<div class="hero-section">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">PN Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">The comprehensive knowledgebase for human proteostasis network genes</p>', unsafe_allow_html=True)

# Search area mimicking the image search bar
search_col1, search_col2, search_col3 = st.columns([1, 3, 1])
with search_col2:
    search_query = st.text_input("", placeholder="Search by Gene Symbol, UniProt ID, or Branch...", label_visibility="collapsed").strip().upper()
st.markdown('</div>', unsafe_allow_html=True)

# 5. Filter & Display Logic
if search_query:
    # Search across multiple columns for a "Smart Search" feel
    results = df[
        df['Gene Symbol'].str.upper().str.contains(search_query, na=False) | 
        df['UniProt ID'].str.upper().str.contains(search_query, na=False) |
        df['Branch'].str.upper().str.contains(search_query, na=False)
    ]
    
    if not results.empty:
        st.markdown(f"### Search Results for \"{search_query}\"")
        st.write(f"Showing {len(results)} results")
        
        # Display Table like PhaSepDB
        display_df = results[['UniProt ID', 'Gene Symbol', 'Gene Name', 'Branch', 'Class', 'Group']]
        
        # Clicking a row is simulated by a selectbox below the table
        selected_gene = st.selectbox("Select a gene from results to view 3D structure:", results['Gene Symbol'].unique())
        selected_row = results[results['Gene Symbol'] == selected_gene].iloc[0]

        # --- Detail Section ---
        st.divider()
        col_info, col_viz = st.columns([1, 2])
        
        with col_info:
            st.subheader(f"🧬 {selected_row['Gene Symbol']}")
            st.write(f"**Full Name:** {selected_row['Gene Name']}")
            st.write(f"**UniProt:** `{selected_row['UniProt ID']}`")
            st.info(f"**Branch:** {selected_row['Branch']}\n\n**Class:** {selected_row['Class']}\n\n**Group:** {selected_row['Group']}")
            
            uniprot_id = selected_row['UniProt ID']
            st.markdown(f"[🔗 UniProt Entry](https://www.uniprot.org/uniprotkb/{uniprot_id}/entry)")
            st.markdown(f"[🔗 AlphaFold Structure](https://alphafold.ebi.ac.uk/entry/{uniprot_id})")

        with col_viz:
            def render_alphafold(uid):
                pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uid}-F1-model_v4.pdb"
                res = requests.get(pdb_url)
                if res.status_code == 200:
                    view = py3Dmol.view(width=800, height=500)
                    view.addModel(res.text, 'pdb')
                    view.setStyle({'cartoon': {'color': 'spectrum'}})
                    view.zoomTo()
                    return view
                return None

            with st.spinner("Loading 3D Model..."):
                view = render_alphafold(uniprot_id)
                if view:
                    showmol(view, height=500, width=800)
                else:
                    st.warning("3D Structure not available.")
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.error("No results found. Please try another search term.")
else:
    # Default view: show a few examples like the image buttons
    st.markdown("<p style='text-align:center; color:white;'>Try searching for: <b>HSPA1A</b>, <b>DNAJA1</b>, or <b>Chaperone</b></p>", unsafe_allow_html=True)