import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Set page configuration
st.set_page_config(
    page_title="Dashboard Universitas Global",
    page_icon="🎓",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("wikidata_universities_sample.csv")
    # Clean inception date to extract year
    df['INCEPTION_YEAR'] = pd.to_datetime(df['INCEPTION'], errors='coerce').dt.year
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Pastikan file 'wikidata_universities_sample.csv' berada di folder yang sama. Error: {e}")
    st.stop()

# Header Aplikasi
st.title("🎓 Dashboard Analisis Data Universitas Global")
st.markdown("Aplikasi ini menganalisis data sampel universitas di seluruh dunia yang bersumber dari Wikidata.")

# Sidebar Filters
st.sidebar.header("Fiter Data")

# Filter Negara
countries = sorted(df['COUNTRYLABEL'].dropna().unique())
selected_countries = st.sidebar.multiselect("Pilih Negara", options=countries, default=countries[:5] if len(countries) > 5 else countries)

# Filter Tahun Berdiri
min_year = int(df['INCEPTION_YEAR'].min()) if not pd.isna(df['INCEPTION_YEAR'].min()) else 1000
max_year = int(df['INCEPTION_YEAR'].max()) if not pd.isna(df['INCEPTION_YEAR'].max()) else 2026
selected_years = st.sidebar.slider("Tahun Berdiri (Inception)", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Apply Filters
filtered_df = df[df['COUNTRYLABEL'].isin(selected_countries)]
filtered_df = filtered_df[(filtered_df['INCEPTION_YEAR'] >= selected_years[0]) & (filtered_df['INCEPTION_YEAR'] <= selected_years[1])]

# Main Metrics Layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Universitas Terfilter", len(filtered_df))
with col2:
    st.metric("Jumlah Negara Terpilih", filtered_df['COUNTRYLABEL'].nunique())
with col3:
    st.metric("Universitas Tertua di Filter", int(filtered_df['INCEPTION_YEAR'].min()) if len(filtered_df) > 0 and not pd.isna(filtered_df['INCEPTION_YEAR'].min()) else "-")

st.markdown("---")

# Visualizations Section
st.subheader("📊 Visualisasi & Analisis")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Top Negara Berdasarkan Jumlah Universitas")
    top_countries = filtered_df['COUNTRYLABEL'].value_counts().reset_index()
    top_countries.columns = ['Negara', 'Jumlah']
    fig_bar = px.bar(top_countries.head(10), x='Jumlah', y='Negara', orientation='h', 
                     title="10 Negara Teratas", color='Jumlah', color_continuous_scale='Blues')
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.markdown("### Tren Pendirian Universitas Seiring Waktu")
    year_trends = filtered_df.dropna(subset=['INCEPTION_YEAR']).groupby('INCEPTION_YEAR').size().reset_index(name='Jumlah')
    fig_line = px.line(year_trends, x='INCEPTION_YEAR', y='Jumlah', title="Tren Pendirian",
                       labels={'INCEPTION_YEAR': 'Tahun', 'Jumlah': 'Jumlah Universitas'})
    st.plotly_chart(fig_line, use_container_width=True)

# Map Section (Geospatial)
st.subheader("🗺️ Peta Sebaran Universitas")
st.markdown("Menampilkan lokasi universitas berdasarkan titik koordinat yang tersedia.")

def parse_coord(coord_str):
    try:
        if pd.isna(coord_str): return None, None
        # Extract numbers inside Point(lon lat)
        match = re.search(r'Point\(([-\d\.]+)\s+([-\d\.]+)\)', str(coord_str))
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            return lat, lon
    except:
        pass
    return None, None

# Apply coordinate parsing
coords = filtered_df['COORD'].apply(parse_coord)
filtered_df['latitude'] = [c[0] for c in coords]
filtered_df['longitude'] = [c[1] for c in coords]

map_df = filtered_df.dropna(subset=['latitude', 'longitude'])

if not map_df.empty:
    st.map(map_df[['latitude', 'longitude']])
else:
    st.info("Tidak ada data koordinat yang valid untuk filter yang dipilih.")

# Data Table Section
st.subheader("📋 Eksplorasi Data Mentah")
st.dataframe(filtered_df[['UNIVERSITYLABEL', 'COUNTRYLABEL', 'INCEPTION_YEAR', 'COORD']], use_container_width=True)
