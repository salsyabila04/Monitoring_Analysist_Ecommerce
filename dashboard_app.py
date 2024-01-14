import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Dashboard Monitoring", page_icon=":bar_chart:",layout="wide")

# Baca data
data_transaksi = pd.read_csv(r'datatransaksi2023.csv')
data_produksi = pd.read_csv(r'dataproduk2023.csv')
data_user = pd.read_csv(r'datauser2023.csv')


# Menampilkan style.css
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# Judul Dashboard
st.title(":bar_chart: Dashboard Monitoring and Ecommerce Analysis")

# Merge DataFrames
merged_data = pd.merge(data_transaksi, data_produksi, on='Product_ID', how='left')

# Hitung rata-rata pendapatan
rata_pendapatan = data_produksi['HARGA_SATUAN'].mean()

# Hitung jumlah pendapatan per bulan
merged_data['Total_Pendapatan'] = merged_data['Quantity'] * merged_data.get('HARGA_SATUAN', rata_pendapatan)

# Explicitly convert 'Date' to datetime
merged_data['Date'] = pd.to_datetime(merged_data['Date'])

# Mengelompokkan data
per_bulan = merged_data.groupby(merged_data['Date'].dt.to_period("M")).agg({'Total_Pendapatan': 'sum'}).reset_index()

# Temukan tanggal dengan jumlah penjualan dan pendapatan terbanyak
pendapatan_terendah = per_bulan.loc[per_bulan['Total_Pendapatan'].idxmin()]
pendapatan_terbanyak = per_bulan.loc[per_bulan['Total_Pendapatan'].idxmax()]

# Sidebar Layout
st.sidebar.title("Pendapatan Terbanyak dan Terendah Perusahaan")

# Visualisasi Pendapatan Terendah
with st.sidebar:
    st.subheader("Pendapatan Terendah")
    st.write(f"Periode: {pendapatan_terendah['Date']}")
    st.write(f"Total Pendapatan: {pendapatan_terendah['Total_Pendapatan']}")

# Visualisasi Pendapatan Terbanyak
with st.sidebar:
    st.subheader("Pendapatan Terbanyak")
    st.write(f"Periode: {pendapatan_terbanyak['Date']}")
    st.write(f"Total Pendapatan: {pendapatan_terbanyak['Total_Pendapatan']}")

# Konfigurasi data transaksi
data_transaksi['Date'] = pd.to_datetime(data_transaksi['Date'])
data_transaksi.set_index('Date', inplace=True)

if not isinstance(data_transaksi.index, pd.DatetimeIndex):
    data_transaksi.index = pd.to_datetime(data_transaksi.index)

transaksi_tiap_bulan = data_transaksi.resample('M').size()
# Visualisasi Jumlah Transaksi per Bulan
col1, col2 = st.columns((2))

with col1:
    st.subheader('Tren Jumlah Transaksi per Bulan')
    fig, ax = plt.subplots(figsize=(10, 6))
    transaksi_tiap_bulan.plot(ax=ax, marker='o')
    plt.title('Tren Jumlah Transaksi per Bulan')
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Transaksi')
    st.pyplot(fig)

# Jumlah Transaksi Tiap Bulan
with col2:
    st.subheader('Jumlah Transaksi Tiap Bulan')
    st.write(transaksi_tiap_bulan)

#Pendapatan setiap bulan
st.subheader("Total Pendapatan per Bulan")
fig, ax = plt.subplots(figsize=(8, 6))
per_bulan.plot(x='Date', y='Total_Pendapatan', kind='bar', ax=ax)
plt.title('Total Pendapatan per Bulan')
plt.xlabel('Bulan')
plt.ylabel('Total Pendapatan')
st.pyplot(fig)



# Merge DataFrames
df_merged = pd.merge(pd.merge(data_transaksi, data_user, on='User_ID'), data_produksi, on='Product_ID')

# Grouping user_id dan product_id
df_grouped = df_merged.groupby(['User_ID', 'Product_ID']).size().reset_index(name='Jumlah_Transaksi')

df_sorted = df_grouped.sort_values(by='Jumlah_Transaksi', ascending=False)

# Visualisasi menggunakan Plotly
fig = px.bar(df_sorted, x='User_ID', y='Jumlah_Transaksi', color='Product_ID', title='Jumlah Transaksi per User dan Produk', labels={'Jumlah_Transaksi': 'Jumlah Transaksi', 'User_ID': 'User ID'}, template="gridon")

# Tampilkan Grafik dalam Streamlit
st.plotly_chart(fig)

# Visualisasi User dengan Jumlah Transaksi Terbanyak menggunakan Seaborn
df_sorted = df_grouped.sort_values(by='Jumlah_Transaksi', ascending=False)
# Jumlah Transaksi untuk Setiap Produk
produk_count = data_transaksi['Product_ID'].value_counts()
cl1, cl2 = st.columns((2))

with cl1:
    st.subheader('User dengan Jumlah Transaksi Terbanyak')
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x='User_ID', y='Jumlah_Transaksi', data=df_sorted.head(), palette='viridis', ax=ax)
    plt.title('User dengan Jumlah Transaksi Terbanyak')
    plt.xlabel('User_ID')
    plt.ylabel('Jumlah Transaksi')
    st.pyplot(fig)

with cl2:
    st.subheader('Jumlah Transaksi untuk Setiap Produk:')
    st.write(produk_count)

# Visualisasi Jumlah Transaksi untuk Setiap Produk menggunakan Seaborn
df_merged['Total_Pendapatan'] = df_merged['Quantity'] * df_merged['HARGA_SATUAN']

# Menghitung total pendapatan untuk setiap produk
produk_teratas = df_merged.groupby('Product_ID')['Total_Pendapatan'].sum().reset_index()

# Mengurutkan DataFrame berdasarkan total pendapatan secara descending
produk_teratas = produk_teratas.sort_values(by='Total_Pendapatan', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='Product_ID', y='Total_Pendapatan', data=produk_teratas, palette='magma')
plt.title('Produk Teratas berdasarkan Jumlah Pendapatan')
plt.xlabel('Product_ID')
plt.ylabel('Total Pendapatan (Rupiah)')
plt.xticks(ha='right')
st.pyplot(fig)


# Jumlah setiap status user
status_count = data_user['Status'].value_counts()

# Tampilkan Dashboard Streamlit

# Visualisasi Distribusi Status User menggunakan Pie Chart

st.subheader('Distribusi Status User')
fig, ax = plt.subplots(figsize=(5, 5))  # Increase the figure size for better visibility
explode = (0, 0.1)
plt.pie(status_count, labels=status_count.index, autopct='%1.1f%%', startangle=140, colors=['skyblue', 'lightcoral'], explode=explode)
plt.tight_layout()
st.pyplot(fig)

# Informasi Harga Termahal
indeks_harga_termahal = data_produksi['HARGA_SATUAN'].idxmax()
harga_termahal = data_produksi.loc[indeks_harga_termahal, 'HARGA_SATUAN']
product_id_termahal = data_produksi.loc[indeks_harga_termahal, 'Product_ID']


st.subheader('Informasi Harga Termahal:')
st.write(f'Harga Termahal: {harga_termahal}')
st.write(f'Product_ID Termahal: {product_id_termahal}')

# Visualisasi Harga Satuan menggunakan Bar Chart
st.subheader('Visualisasi Harga Satuan')
st.bar_chart(data_produksi[['Product_ID', 'HARGA_SATUAN']].set_index('Product_ID'))

# Data Produksi
# st.subheader('Data Produksi:')
# st.write(data_produksi)

# Jumlah Produk Terjual dan Terlaris
jumlah_produk_terjual = data_transaksi.groupby('Product_ID')['Quantity'].sum().reset_index(name='Jumlah_Produk_Terjual')

# Sorting berdasarkan jumlah produk terjual
jumlah_produk_terjual = jumlah_produk_terjual.sort_values(by='Jumlah_Produk_Terjual', ascending=False)

# Menghitung produk terlaris (produk dengan jumlah penjualan tertinggi)
produk_terlaris = jumlah_produk_terjual.iloc[0]['Product_ID']
jumlah_terlaris = jumlah_produk_terjual.iloc[0]['Jumlah_Produk_Terjual']

# Menghitung produk dengan penjualan terendah (produk dengan jumlah penjualan terendah)
produk_terendah = jumlah_produk_terjual.iloc[-1]['Product_ID']
jumlah_terendah = jumlah_produk_terjual.iloc[-1]['Jumlah_Produk_Terjual']

st.write(f'Produk terendah: {produk_terendah}')
st.write(f'Produk terlaris : {produk_terlaris}')

# Visualisasi Distribusi Jumlah Produk Terlaris dan Terendah menggunakan Pie Chart
data_pie = [jumlah_terlaris, jumlah_terendah]
labels = [f'Produk Terlaris ({produk_terlaris}) - {jumlah_terlaris} pcs', f'Produk Terendah ({produk_terendah}) - {jumlah_terendah} pcs']

fig, ax = plt.subplots(figsize=(8, 8))
plt.pie(data_pie, labels=labels, autopct='%1.1f%%', startangle=140, pctdistance=0.85, colors=['skyblue', 'pink'], explode=explode)
plt.title('Distribusi Jumlah Produk Terlaris dan Terendah')
st.pyplot(fig)

# Analisis Frekuensi Rentang Umur yang Melakukan Transaksi
df_merged = pd.merge(data_transaksi, data_user, on='User_ID')

# Menghitung frekuensi setiap nilai umur
frekuensi_umur = df_merged['Age'].value_counts().sort_index()

# Palet warna untuk bar chart
palet_warna = sns.color_palette("pastel", n_colors=len(frekuensi_umur))


st.subheader('Frekuensi Rentang Umur yang Melakukan Transaksi')
fig, ax = plt.subplots(figsize=(8, 6))
plt.bar(frekuensi_umur.index, frekuensi_umur.values, color=palet_warna)
plt.title('Frekuensi Rentang Umur yang Melakukan Transaksi')
plt.xlabel('Rentang Umur')
plt.ylabel('Frekuensi')
st.pyplot(fig)

# WordCloud Transaksi
transaksi_text = ' '.join(data_transaksi['Transaction_ID'].astype(str))

# Membuat WordCloud
wordcloud = WordCloud(width=880, height=440, background_color='white').generate(transaksi_text)
st.image(wordcloud.to_image())

