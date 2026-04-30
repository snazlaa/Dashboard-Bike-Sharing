import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    df_day  = pd.read_csv('day.csv')
    df_hour = pd.read_csv('hour.csv')
    
    def clean_dataset(df, is_hour=False):
        df = df.copy()
        df['dteday'] = pd.to_datetime(df['dteday'])
        df['season'] = df['season'].map({
            1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
        }).astype('category')
        df['yr'] = df['yr'].map({0: 2011, 1: 2012}).astype('category')
        df['mnth'] = df['mnth'].map({
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }).astype('category')
        df['holiday'] = df['holiday'].map({0: 'No', 1: 'Yes'}).astype('category')
        df['weekday'] = df['weekday'].map({
            0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed',
            4: 'Thu', 5: 'Fri', 6: 'Sat'
        }).astype('category')
        df['workingday'] = df['workingday'].map({0: 'No', 1: 'Yes'}).astype('category')
        df['weathersit'] = df['weathersit'].map({
            1: 'Clear', 2: 'Mist',
            3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'
        }).astype('category')
        if is_hour:
            df['hr'] = df['hr'].astype('category')
        return df
    
    df_day  = clean_dataset(df_day,  is_hour=False)
    df_hour = clean_dataset(df_hour, is_hour=True)
    
    df_day['usage_cluster'] = pd.cut(
        df_day['cnt'],
        bins=[0, 2500, 5000, 8714],
        labels=['Low Usage', 'Medium Usage', 'High Usage']
    )
    
    return df_day, df_hour

df_day, df_hour = load_data()

# Header
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis pola peminjaman sepeda di Washington D.C. periode 2011–2012")
st.divider()

#  Sidebar Filter
st.sidebar.header("🔍 Filter Data")

year_option = st.sidebar.multiselect(
    "Pilih Tahun",
    options=[2011, 2012],
    default=[2011, 2012]
)

season_option = st.sidebar.multiselect(
    "Pilih Musim",
    options=['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

# Apply Filter
df_day_filtered  = df_day[
    (df_day['yr'].astype(int).isin(year_option)) &
    (df_day['season'].isin(season_option))
]
df_hour_filtered = df_hour[
    (df_hour['yr'].astype(int).isin(year_option)) &
    (df_hour['season'].isin(season_option))
]

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Peminjaman", f"{df_day_filtered['cnt'].sum():,.0f}")
with col2:
    st.metric("Rata-rata Harian", f"{df_day_filtered['cnt'].mean():,.0f}")
with col3:
    st.metric("Total Pengguna Casual", f"{df_day_filtered['casual'].sum():,.0f}")
with col4:
    st.metric("Total Pengguna Registered", f"{df_day_filtered['registered'].sum():,.0f}")

st.divider()

# PERTANYAAN 1
st.subheader("📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Peminjaman Sepeda")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# per musim
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_stats = df_day_filtered.groupby('season', observed=True)[['casual', 'registered']].mean().reindex(season_order)
season_stats.plot(kind='bar', ax=axes[0], color=['#42A5F5', '#1A237E'], edgecolor='white', width=0.6)
axes[0].set_title('Rata-rata Peminjaman per Musim', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Musim', fontsize=10)
axes[0].set_ylabel('Rata-rata Peminjaman per Hari', fontsize=10)
axes[0].set_xticklabels(season_order, rotation=0)
axes[0].legend(['Casual', 'Registered'], title='Tipe Pengguna')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
axes[0].set_ylim(0, season_stats.values.max() * 1.15)
for container in axes[0].containers:
    axes[0].bar_label(container, fmt='%.0f', padding=3, fontsize=8)

# per cuaca
weather_order = ['Clear', 'Mist', 'Light Snow/Rain']
weather_stats = df_day_filtered.groupby('weathersit', observed=True)[['casual', 'registered']].mean().reindex(weather_order)
weather_stats.plot(kind='bar', ax=axes[1], color=['#42A5F5', '#1A237E'], edgecolor='white', width=0.6)
axes[1].set_title('Rata-rata Peminjaman per Kondisi Cuaca', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Kondisi Cuaca', fontsize=10)
axes[1].set_ylabel('Rata-rata Peminjaman per Hari', fontsize=10)
axes[1].set_xticklabels(weather_order, rotation=0)
axes[1].legend(['Casual', 'Registered'], title='Tipe Pengguna')
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
axes[1].set_ylim(0, weather_stats.values.max() * 1.15)
for container in axes[1].containers:
    axes[1].bar_label(container, fmt='%.0f', padding=3, fontsize=8)

plt.tight_layout()
st.pyplot(fig)
plt.close()

# PERTANYAAN 2
st.subheader("⏰ Pertanyaan 2: Pola Peminjaman Berdasarkan Waktu")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# per jam
hour_workingday = df_hour_filtered.groupby(
    ['hr', 'workingday'], observed=True
)['cnt'].mean().reset_index()
hour_workingday['hr'] = hour_workingday['hr'].astype(int)

working = hour_workingday[hour_workingday['workingday'] == 'Yes']
holiday = hour_workingday[hour_workingday['workingday'] == 'No']

axes[0].plot(working['hr'], working['cnt'], color='#1A237E', marker='o', markersize=4, linewidth=2, label='Hari Kerja')
axes[0].plot(holiday['hr'], holiday['cnt'], color='#EF5350', marker='o', markersize=4, linewidth=2, label='Hari Libur')
axes[0].set_title('Pola Peminjaman per Jam\n(Hari Kerja vs Hari Libur)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Jam', fontsize=10)
axes[0].set_ylabel('Rata-rata Peminjaman per Jam', fontsize=10)
axes[0].set_xticks(range(0, 24))
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
axes[0].axvline(x=8,  color='#1A237E', linestyle='--', alpha=0.4)
axes[0].axvline(x=17, color='#1A237E', linestyle='--', alpha=0.4)
axes[0].annotate('Peak Pagi\n(08.00)', xy=(8, working[working['hr']==8]['cnt'].values[0]),
                 xytext=(9, working[working['hr']==8]['cnt'].values[0] + 20),
                 fontsize=8, color='#1A237E',
                 arrowprops=dict(arrowstyle='->', color='#1A237E', lw=1))
axes[0].annotate('Peak Sore\n(17.00)', xy=(17, working[working['hr']==17]['cnt'].values[0]),
                 xytext=(18, working[working['hr']==17]['cnt'].values[0] + 20),
                 fontsize=8, color='#1A237E',
                 arrowprops=dict(arrowstyle='->', color='#1A237E', lw=1))
axes[0].legend(title='Tipe Hari')

# per hari
weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekday_stats = df_day_filtered.groupby('weekday', observed=True)['cnt'].mean().reindex(weekday_order)
colors_wd = ['#1A237E'] * 5 + ['#EF5350'] * 2
axes[1].bar(weekday_stats.index, weekday_stats.values, color=colors_wd, edgecolor='white', width=0.6)
axes[1].set_title('Rata-rata Peminjaman\nper Hari dalam Seminggu', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Hari', fontsize=10)
axes[1].set_ylabel('Rata-rata Peminjaman per Hari', fontsize=10)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
axes[1].set_ylim(0, weekday_stats.max() * 1.12)
axes[1].bar_label(axes[1].containers[0], fmt='%.0f', padding=3, fontsize=8)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#1A237E', label='Hari Kerja'),
                   Patch(facecolor='#EF5350', label='Akhir Pekan')]
axes[1].legend(handles=legend_elements, title='Tipe Hari')

plt.tight_layout()
st.pyplot(fig)
plt.close()

# CLUSTERING
st.subheader("🔬 Advanced Analysis: Clustering Tingkat Penggunaan Sepeda")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
colors_cluster = ['#EF5350', '#FFA726', '#66BB6A']

# Distribusi cluster
cluster_counts = df_day_filtered['usage_cluster'].value_counts().reindex(
    ['Low Usage', 'Medium Usage', 'High Usage']
)
axes[0].bar(cluster_counts.index, cluster_counts.values, color=colors_cluster, edgecolor='white', width=0.6)
axes[0].set_title('Distribusi Cluster Penggunaan', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Cluster', fontsize=10)
axes[0].set_ylabel('Jumlah Hari', fontsize=10)
axes[0].set_ylim(0, cluster_counts.max() * 1.15)
axes[0].bar_label(axes[0].containers[0], fmt='%d', padding=3, fontsize=10)

# Cluster per musim
season_cluster = pd.crosstab(df_day_filtered['season'], df_day_filtered['usage_cluster'])
season_cluster = season_cluster.reindex(columns=['Low Usage', 'Medium Usage', 'High Usage'])
season_cluster = season_cluster.reindex(['Spring', 'Summer', 'Fall', 'Winter'])
season_cluster.plot(kind='bar', ax=axes[1], stacked=True, color=colors_cluster, edgecolor='white', width=0.6)
axes[1].set_title('Komposisi Cluster per Musim', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Musim', fontsize=10)
axes[1].set_ylabel('Jumlah Hari', fontsize=10)
axes[1].set_xticklabels(['Spring', 'Summer', 'Fall', 'Winter'], rotation=0)
axes[1].legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
for c in axes[1].containers:
    axes[1].bar_label(c, fmt='%d', label_type='center', fontsize=8, color='white', fontweight='bold')

# Cluster per cuaca
weather_cluster = pd.crosstab(df_day_filtered['weathersit'], df_day_filtered['usage_cluster'])
weather_cluster = weather_cluster.reindex(columns=['Low Usage', 'Medium Usage', 'High Usage'])
weather_cluster = weather_cluster.reindex(['Clear', 'Mist', 'Light Snow/Rain'])
weather_cluster.plot(kind='bar', ax=axes[2], stacked=True, color=colors_cluster, edgecolor='white', width=0.6)
axes[2].set_title('Komposisi Cluster per Kondisi Cuaca', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Kondisi Cuaca', fontsize=10)
axes[2].set_ylabel('Jumlah Hari', fontsize=10)
axes[2].set_xticklabels(['Clear', 'Mist', 'Light Snow/Rain'], rotation=0)
axes[2].legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
for c in axes[2].containers:
    axes[2].bar_label(c, fmt='%d', label_type='center', fontsize=8, color='white', fontweight='bold')

plt.tight_layout()
st.pyplot(fig)
plt.close()

# Footer
st.divider()
st.caption("Dashboard dibuat untuk submission Dicoding — Bike Sharing Dataset (2011–2012)")