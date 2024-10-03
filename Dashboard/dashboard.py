# Import libraries
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv('D:/Bangkit/submission/dashboard/combined_data_airquality.csv')

# Function to preprocess date data
def data_date(df):
    # change the year, month, and day into one column and convert it to datetime format
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']])
    return df

df = data_date(df)

# Sidebar filters
st.sidebar.header('Filter Data')
stations = df['station'].unique()
selected_station = st.sidebar.selectbox('Pilih Stasiun', stations)

# Filter dataframe based on selected station
df_filtered = df[df['station'] == selected_station]

# Function to plot PM2.5 and PM10 distribution with bins slider
def plot_pm_distribution(df):
    bins = st.sidebar.slider('Jumlah bins untuk histogram', min_value=10, max_value=50, value=30)
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    # Plot PM2.5 distribution
    sns.histplot(df['PM2.5'], bins=bins, ax=ax[0], color='blue')
    ax[0].set_title(f'Distribusi PM2.5 - {selected_station}')

    # Plot PM10 distribution
    sns.histplot(df['PM10'], bins=bins, ax=ax[1], color='green')
    ax[1].set_title(f'Distribusi PM10 - {selected_station}')

    st.pyplot(fig)

# Function to calculate and plot correlation
def plot_correlation(df):
    corr = df[['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'WSPM']].corr()

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title(f'Korelasi antara Polutan dan Faktor Meteorologi - {selected_station}')

    st.pyplot(fig)

# Function to find the city/station with highest pollution
def highest_pollution_station(df):
    pollution_station = df.groupby('station')['PM2.5'].mean().reset_index()
    highest_station = pollution_station.sort_values('PM2.5', ascending=False).iloc[0]
    st.write(f"Stasiun dengan tingkat polusi PM2.5 tertinggi adalah: {highest_station['station']} dengan nilai rata-rata PM2.5: {highest_station['PM2.5']}")

# Function to plot seasonal trends with month filter
def plot_seasonal_trends(df):
    df['month'] = pd.to_datetime(df['datetime']).dt.month

    # Add slider for selecting specific months
    months = st.sidebar.multiselect('Pilih Bulan', options=list(range(1, 13)), default=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    if len(months) > 0:
        df_filtered = df[df['month'].isin(months)]
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='month', y='PM2.5', data=df_filtered, marker='o', label='PM2.5')
        sns.lineplot(x='month', y='PM10', data=df_filtered, marker='o', label='PM10')
        
        ax.set_title(f'Tren Musiman PM2.5 dan PM10 - {selected_station}')
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Tingkat Polutan')
        st.pyplot(fig)
    else:
        st.write("Pilih setidaknya satu bulan untuk melihat tren musiman.")

# Function to plot time trends with date range filter
# Function to plot time trends with date range filter
def plot_time_trends(df):
    df['date'] = pd.to_datetime(df['datetime']).dt.date  # Menggunakan .date() untuk mengubah format ke tanggal

    # Add date range slider
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

    if start_date and end_date:
        # Ubah pd.to_datetime menjadi hanya date untuk konsistensi perbandingan
        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        daily_avg = df_filtered.groupby('date')[['PM2.5', 'PM10']].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='date', y='PM2.5', data=daily_avg, label='PM2.5')
        sns.lineplot(x='date', y='PM10', data=daily_avg, label='PM10')

        ax.set_title(f'Tren Harian PM2.5 dan PM10 - {selected_station}')
        ax.set_xlabel('Tanggal')
        ax.set_ylabel('Tingkat Polutan')
        st.pyplot(fig)
    else:
        st.write("Pilih rentang tanggal untuk melihat tren waktu.")

# Streamlit interface
st.title("Dashboard Interaktif Analisis Kualitas Udara")

# Sidebar options
option = st.sidebar.selectbox('Pilih Analisis', [
    'Distribusi PM2.5 dan PM10',
    'Korelasi Faktor Meteorologi dengan Polutan',
    'Stasiun dengan Tingkat Polusi Tertinggi',
    'Tren Musiman Kualitas Udara',
    'Tren Waktu Kualitas Udara'
])

# Show different analysis based on selection
if option == 'Distribusi PM2.5 dan PM10':
    st.header(f"Distribusi PM2.5 dan PM10 di {selected_station}")
    plot_pm_distribution(df_filtered)

elif option == 'Korelasi Faktor Meteorologi dengan Polutan':
    st.header(f"Korelasi Faktor Meteorologi dengan Polutan di {selected_station}")
    plot_correlation(df_filtered)

elif option == 'Stasiun dengan Tingkat Polusi Tertinggi':
    st.header("Stasiun dengan Tingkat Polusi Tertinggi")
    highest_pollution_station(df)

elif option == 'Tren Musiman Kualitas Udara':
    st.header(f"Tren Musiman Kualitas Udara di {selected_station}")
    plot_seasonal_trends(df_filtered)

elif option == 'Tren Waktu Kualitas Udara':
    st.header(f"Tren Waktu Kualitas Udara di {selected_station}")
    plot_time_trends(df_filtered)
