# Impor library yang digunakan
import streamlit as st                             # Buat aplikasi web
import pandas as pd                                # Manipulasi data
import numpy as np                                 # Manipulasi data
from sklearn.preprocessing import StandardScaler   # Pemrosesan data untuk clustering
from sklearn.cluster import KMeans                 # Pemrosesan data untuk clustering
import plotly.express as px                        # Membuat grafik interaktif
import plotly.graph_objects as go                  # Membuat grafik interaktif
from plotly.subplots import make_subplots          # Membuat grafik interaktif
from PIL import Image                              # Membuka gambar

# Konfigurasi judul halaman streamlit 
st.set_page_config(page_title="Analisis Penyewaan Sepeda", layout="wide")

# Fungsi untuk menghitung RFM, apakah hari tersebut hari kerja atau bukan
def calculate_rfm(data, is_workday):
    subset = data[data['workingday'] == is_workday]
    max_date = pd.to_datetime(subset['dteday']).max()
    recency = (max_date - pd.to_datetime(subset['dteday'])).dt.days                            # Selisih hari tanggal data maksimal dengan tanggal setiap record
    frequency = subset.groupby(pd.to_datetime(subset['dteday']).dt.month)['cnt'].count()       # Jumlah transaksi per bulan
    monetary = subset['cnt']                                                                   # Jumlah sepeda yang disewa
    return recency, frequency, monetary

# Fungsi untuk melakukan clustering data berdasarkan jam dan jumlah penyewa sepeda
def perform_clustering(df):
    data_cluster = df.groupby('hr')[['cnt']].mean().reset_index()
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_cluster)
    kmeans = KMeans(n_clusters=3, random_state=42)
    data_cluster['cluster'] = kmeans.fit_predict(data_scaled)
    return data_cluster

# Mendefinisikan fungsi utama yang menjalankan seluruh program di dalamnya
def main():
    
    # Membuat sidebar 
    with st.sidebar:
        # Menampilkan foto bike sharing
        st.image("https://raw.githubusercontent.com/ArbazFerdiansah/desktop-tutorial/refs/heads/main/bike_sharing.webp?token=GHSAT0AAAAAACYPLNACXCHFB6QUCCHCHGZWZZKIC5A", use_column_width=True)
        
        # Menampilkan teks
        st.title("Analisis Penyewaan Sepeda")
        st.write("Arbaz Ferdiansah")
        st.text(2024)
    
    # Membuat judul dashboard
    st.title("Dashboard Analisis Penyewaan Sepeda 🚲")    
    
    # Membaca data dari file "clustering_results.xls" dan "rfm_results.xls"
    # Tanpa penanganan kesalahan
    clustering_df = pd.read_excel('/path/to/your/file/clustering_results.xls')
    rfm_df = pd.read_excel('/path/to/your/file/rfm_results.xls')
    
    # Membuat dua tab untuk navigasi clustering dan RFM
    tab1, tab2 = st.tabs(["Analisis Clustering", "Analisis RFM"])
    
    # Tab 1: Analisis Clustering
    with tab1:
        # Membuat header untuk tab 1
        st.header("Pola Penggunaan Sepeda Berdasarkan Jam")
        
        # Memanggil fungsi perform_clustering untuk melakukan clustering pada data
        data_cluster = perform_clustering(clustering_df)
        
        # Membuat scatter plot yang menunjukkan penggunaan sepeda per jam dengan plotly 
        fig_cluster = px.scatter(data_cluster, 
                               x='hr', 
                               y='cnt',
                               color='cluster',
                               title='Clustering Penggunaan Sepeda per Jam',
                               labels={'hr': 'Jam', 'cnt': 'Rata-rata Jumlah Sepeda'})
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        # Menampilkan karakteristik tiap cluster dengan 3 kolom 
        # Membuat subheader untuk menampilkan karakteristik setiap cluster
        st.subheader("Karakteristik Cluster")
        col1, col2, col3 = st.columns(3)
        
        for cluster in range(3):
            cluster_data = data_cluster[data_cluster['cluster'] == cluster]
            with eval(f"col{cluster+1}"):
                st.metric(
                    label=f"Cluster {cluster}",                                          # Setiap cluster
                    value=f"{cluster_data['cnt'].mean():.0f} sepeda",                    # Rata-rata jumlah sepeda tiap cluster
                    delta=f"Jam {', '.join(map(str, cluster_data['hr'].tolist()))}"      # Jam di mana cluster tersebut dominan
                )
    
    # Tab 2: Analisis RFM
    with tab2:
        # Membuat header untuk tab 2
        st.header("Analisis RFM: Hari Kerja vs Akhir Pekan")
        
        # Menghitung nilai RFM dengan fungsi calculate_rfm untuk hari kerja(1) dan akhir pekan(0)
        r_work, f_work, m_work = calculate_rfm(rfm_df, 1)
        r_weekend, f_weekend, m_weekend = calculate_rfm(rfm_df, 0)
        
        # Membuat subplots  dengan 3 kolom
        fig = make_subplots(rows=1, cols=3, 
                          subplot_titles=('Distribusi Jumlah Penggunaan', 
                                        'Rata-rata Frequency per Bulan',
                                        'Rata-rata Recency (Hari)'))
        
        # Kolom 1 : membuat box plot untuk membandingkan jumlah pengguna sepeda antara hari kerja dan akhir pekan
        fig.add_trace(
            go.Box(y=m_work, name='Hari Kerja', showlegend=False),
            row=1, col=1
        )
        fig.add_trace(
            go.Box(y=m_weekend, name='Akhir Pekan', showlegend=False),
            row=1, col=1
        )
        
        # Kolom 2 : membuat bar chart untuk menampilkan rata-rata frekuensi per bulan
        fig.add_trace(
            go.Bar(x=['Hari Kerja', 'Akhir Pekan'], 
                  y=[f_work.mean(), f_weekend.mean()],
                  showlegend=False),
            row=1, col=2
        )
        
        # Kolom 3 : membuat bar chart untuk menampilkan rata-rata 
        fig.add_trace(
            go.Bar(x=['Hari Kerja', 'Akhir Pekan'], 
                  y=[r_work.mean(), r_weekend.mean()],
                  showlegend=False),
            row=1, col=3
        )
        
        # Menyesuaikan tinggi layout subplot dan menampilkan grafik
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Membuat 2 kolom untuk menampilkan metrik statistik untuk hari kerja dan akhir pekan
        col1, col2 = st.columns(2)
        
        # Kolom 1 : menampilkan statistik penggunaan, frekuensi per bulan, dan recency rata-rata di hari kerja
        with col1:
            st.subheader("Statistik Hari Kerja")
            st.metric("Rata-rata Penggunaan", f"{m_work.mean():.0f} sepeda")
            st.metric("Frequency per Bulan", f"{f_work.mean():.1f} kali")
            st.metric("Rata-rata Recency", f"{r_work.mean():.1f} hari")
        
        # Kolom 2 : menampilkan statistik penggunaan, frekuensi per bulan, dan recency rata-rata di akhir pekan
        with col2:
            st.subheader("Statistik Akhir Pekan")
            st.metric("Rata-rata Penggunaan", f"{m_weekend.mean():.0f} sepeda")
            st.metric("Frequency per Bulan", f"{f_weekend.mean():.1f} kali")
            st.metric("Rata-rata Recency", f"{r_weekend.mean():.1f} hari")
    
    # Menampilkan teks dalam ukuran kecil
    st.caption('Copyright (c) Arbaz 2024')

# Memastikan fungsi main() dijalankan jika skrip dieksekusi  
if __name__ == "__main__":
    main()
