import streamlit as st
import pandas as pd

# Layout beállítása a teljes szélesség használatához
st.set_page_config(layout="wide")

# Reszponzív stílusok
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }        
        .stMarkdown, .stTable, .stDataFrame, .stRadio {
            font-size: 18px !important;
        }
        .stRadio p {
            font-size: 18px !important;
        }    
        .block-container {
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 95%;
        }
        .messier-table {
            width: 100%;
            border-collapse: collapse;
            text-align: center;     
        }
        .messier-table td, .messier-table th {
            padding: 8px;
            border: 1px solid #ddd;
        }
        .messier-table th {
            text-align: center;
        }
        .messier-img {
            width: 320px;
            height: auto;
        }
        .messier-container {
            width: 100%;
            overflow-x: auto;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=604800)  # 7 napos cache
def load_data():
    # CSV betöltése
    df = pd.read_csv('messier_objects.csv')
    # NaN értékek helyettesítése '-' jellel
    return df.fillna('-')

@st.cache_data(ttl=604800)
def generate_table_html(df):
    display_df = df.drop(columns=['Image']) # Az eredeti nagy képek eltávolítása
    display_df = display_df.rename(columns={'Image small': 'Image'})    
    # Képek megjelenítése HTML-ben a DataFrame-ben
    def image_formatter(url):
        return f'<img src="app/{url}" class="messier-img">'
    
    html = display_df.to_html(
        escape=False,
        formatters={'Image': image_formatter},
        index=False,
        classes='messier-table'
    )
    
    return f'<div class="messier-container">{html}</div>'

@st.cache_data(ttl=604800)
def generate_detail_view_html(df):   
    display_df = df.drop(columns=['Image small'])
    for _, row in display_df.iterrows():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(row['Image'], use_column_width=True)
        
        with col2:
            st.write(f"**{row['Messier number']}**")
            if pd.notna(row['Common name']):
                st.write(f"*{row['Common name']}*")
            if pd.notna(row['NGC/IC number']):
                st.write(f"NGC/IC: {row['NGC/IC number']}")
            if pd.notna(row['Object type']):
                st.write(f"Type: {row['Object type']}")
            if pd.notna(row['Distance (kly)']):
                st.write(f"Distance: {row['Distance (kly)']} kly")
            if pd.notna(row['Constellation']):
                st.write(f"Constellation: {row['Constellation']}")
            if pd.notna(row['Apparent magnitude']):
                st.write(f"Magnitude: {row['Apparent magnitude']}")
            if pd.notna(row['Apparent dimensions']):
                st.write(f"Dimensions: {row['Apparent dimensions']}")
            if pd.notna(row['Right ascension']):
                st.write(f"RA: {row['Right ascension']}")
            if pd.notna(row['Declination']):
                st.write(f"Dec: {row['Declination']}")
        
        st.markdown("---")

st.title = "Messier Catalogue"

df = load_data()
    
# Megjelenítési mód választó
display_mode = st.radio("Please select a view:", 
                       ["Table", "Detailed"])

if display_mode == "Table":
    html = generate_table_html(df)
else:
    html = generate_detail_view_html(df)

st.write(html, unsafe_allow_html=True)
