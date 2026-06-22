import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Dashboard Data Mining Bonek", layout="wide")
st.title("⚽ Dashboard Data Mining Suporter Persebaya (Bonek)")

df = pd.read_csv("dataset_suporter_persebaya_100.csv")

st.header("Dataset Suporter")
st.dataframe(df)

st.header("Statistik Deskriptif")
st.write(df.describe())

st.header("Jumlah Suporter per Kota")
kota = df["Kota_Asal"].value_counts().reset_index()
kota.columns = ["Kota", "Jumlah"]
fig1 = px.bar(kota, x="Kota", y="Jumlah")
st.plotly_chart(fig1, use_container_width=True)

st.header("Distribusi Loyalitas")
loyal = df["Loyalitas"].value_counts().reset_index()
loyal.columns = ["Loyalitas", "Jumlah"]
fig2 = px.pie(loyal, names="Loyalitas", values="Jumlah")
st.plotly_chart(fig2, use_container_width=True)

st.header("Clustering K-Means")
fitur = df[["Umur", "Frekuensi_Nonton", "Pengeluaran_Merchandise"]]
scaler = StandardScaler()
X = scaler.fit_transform(fitur)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X)

st.dataframe(df[["ID_Suporter", "Nama", "Cluster"]])

fig3 = px.scatter(
    df,
    x="Frekuensi_Nonton",
    y="Pengeluaran_Merchandise",
    color=df["Cluster"].astype(str),
    hover_data=["Nama"]
)
st.plotly_chart(fig3, use_container_width=True)
