import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. KONFIGURASI HALAMAN & CUSTOM STYLES (CSS)
# ==========================================
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS untuk menghias Header, KPI Cards, dan Chart Titles
st.markdown("""
    <style>
    /* Styling Banner Header Utama */
    .header-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 24px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    .header-banner h1 {
        color: #ffffff !important;
        font-size: 30px !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }
    .header-banner p {
        color: #e0e0e0 !important;
        font-size: 15px !important;
        margin-bottom: 0px !important;
    }
    .status-badge {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-top: 10px;
    }

    /* Styling KPI Custom Cards */
    .kpi-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border-left: 5px solid #1E88E5;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 13px;
        color: #666666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #111111;
        margin: 5px 0;
    }
    .kpi-subtext {
        font-size: 12px;
        color: #888888;
    }

    /* Styling Judul Chart Ke-Highlight */
    .chart-header {
        background-color: #f8f9fa;
        border-left: 5px solid #2980b9;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        font-size: 16px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 15px;
        margin-top: 10px;
    }

    /* Styling Box Insight */
    .insight-box {
        background-color: #eef7fc;
        border: 1px solid #b3e5fc;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        color: #0277bd;
        margin-top: 10px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# Set Seaborn theme global
sns.set_theme(style="whitegrid")

# ==========================================
# 2. LOAD DATASET (CACHING)
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/main_data.zip", compression='zip')
    except FileNotFoundError:
        df = pd.read_csv("main_data.zip", compression='zip')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# ==========================================
# 3. SIDEBAR (FILTER DATA INTERAKTIF)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1163/1163661.png", width=90)
st.sidebar.title("⚙️ Filter Analisis")

min_date = df['datetime'].min().date()
max_date = df['datetime'].max().date()

start_date, end_date = st.sidebar.date_input(
    label="📅 Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

all_stations = sorted(df['station'].unique().tolist())
selected_stations = st.sidebar.multiselect(
    label="📍 Pilih Stasiun Pemantauan:",
    options=all_stations,
    default=all_stations
)

if not selected_stations:
    st.sidebar.warning("Pilih minimal satu stasiun!")
    st.stop()

# Filter Data
filtered_df = df[
    (df['datetime'].dt.date >= start_date) & 
    (df['datetime'].dt.date <= end_date) & 
    (df['station'].isin(selected_stations))
]

# ==========================================
# 4. DEKORASI HEADER UTAMA
# ==========================================
st.markdown(f"""
    <div class="header-banner">
        <h1>🌤️ Beijing Air Quality Analytics Dashboard</h1>
        <p>Eksplorasi Spasial & Temporal Konsentrasi Polutan Partikel Halus (PM<sub>2.5</sub>)</p>
        <span class="status-badge">📍 {len(selected_stations)} Stasiun Terpilih &nbsp;|&nbsp; 📆 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}</span>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. DEKORASI KPI CARDS (TERHIAS)
# ==========================================
avg_pm25 = filtered_df['PM2.5'].mean()
max_pm25 = filtered_df['PM2.5'].max()
cleanest_station = filtered_df.groupby('station')['PM2.5'].mean().idxmin() if not filtered_df.empty else "-"
dirtiest_station = filtered_df.groupby('station')['PM2.5'].mean().idxmax() if not filtered_df.empty else "-"

# Status Udara
if avg_pm25 <= 35:
    aqi_status = "🟢 Baik (Good)"
elif avg_pm25 <= 75:
    aqi_status = "🟡 Sedang (Moderate)"
elif avg_pm25 <= 115:
    aqi_status = "🟠 Tidak Sehat"
else:
    aqi_status = "🔴 Sangat Tidak Sehat"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #1E88E5;">
            <div class="kpi-title">Rerata PM2.5</div>
            <div class="kpi-value">{avg_pm25:.2f} <span style="font-size:14px;">µg/m³</span></div>
            <div class="kpi-subtext">Status: <b>{aqi_status}</b></div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #D32F2F;">
            <div class="kpi-title">PM2.5 Puncak (Max)</div>
            <div class="kpi-value">{max_pm25:.1f} <span style="font-size:14px;">µg/m³</span></div>
            <div class="kpi-subtext">Konsentrasi Maksimum Harian</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #2E7D32;">
            <div class="kpi-title">Stasiun Terbersih</div>
            <div class="kpi-value" style="font-size:20px;">{cleanest_station}</div>
            <div class="kpi-subtext">Rerata Polusi Paling Rendah</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #E65100;">
            <div class="kpi-title">Stasiun Terpolusi</div>
            <div class="kpi-value" style="font-size:20px;">{dirtiest_station}</div>
            <div class="kpi-subtext">Rerata Polusi Paling Tinggi</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. BARIS 1 (2 CHART: SPASIAL & PENGARUH ANGIN)
# ==========================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown('<div class="chart-header">📊 1. Rerata PM2.5 per Stasiun Pemantauan</div>', unsafe_allow_html=True)
    station_pm25 = filtered_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False).reset_index()

    if not station_pm25.empty:
        fig1, ax1 = plt.subplots(figsize=(7, 4.5))
        max_val = station_pm25['PM2.5'].max()
        min_val = station_pm25['PM2.5'].min()
        colors = ['#D32F2F' if x == max_val else ('#2E7D32' if x == min_val else '#72B4EB') for x in station_pm25['PM2.5']]

        sns.barplot(
            x='PM2.5', y='station', hue='station',
            data=station_pm25, palette=colors, legend=False, ax=ax1
        )
        ax1.set_xlabel("Rerata PM2.5 (µg/m³)", fontsize=10)
        ax1.set_ylabel("Stasiun Pemantauan", fontsize=10)
        ax1.axvline(x=75, color='orange', linestyle='--', linewidth=1.5, label='Batas Udara Buruk (>75 µg/m³)')
        ax1.legend(loc='lower right', fontsize=8)
        st.pyplot(fig1)

        st.markdown("""
            <div class="insight-box">
                💡 <b>Insight Spasial:</b> Stasiun <b>Dongsi</b> konsisten mencatatkan polusi tertinggi, sedangkan <b>Dingling</b> menjadi wilayah terbersih karena minim aktivitas industri.
            </div>
        """, unsafe_allow_html=True)

with row1_col2:
    st.markdown('<div class="chart-header">💨 2. Hubungan Kecepatan Angin (WSPM) vs PM2.5</div>', unsafe_allow_html=True)
    
    # Binned WSPM untuk analisis dispersi angin
    filtered_df['wind_speed_bin'] = pd.cut(filtered_df['WSPM'], bins=[0, 1, 2, 4, 15], labels=['Tenang (<1m/s)', 'Pelan (1-2m/s)', 'Sedang (2-4m/s)', 'Kencang (>4m/s)'])
    wspm_pm25 = filtered_df.groupby('wind_speed_bin', observed=False)['PM2.5'].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    sns.barplot(
        x='wind_speed_bin', y='PM2.5', hue='wind_speed_bin',
        data=wspm_pm25, palette='Blues_r', legend=False, ax=ax2
    )
    ax2.set_xlabel("Kategori Kecepatan Angin", fontsize=10)
    ax2.set_ylabel("Rerata PM2.5 (µg/m³)", fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig2)

    st.markdown("""
        <div class="insight-box">
            💡 <b>Insight Dispersi Angin:</b> Saat kecepatan angin sangat pelan (<1 m/s), akumulasi partikel polutan terperangkap di udara. Kecepatan angin di atas 4 m/s efektif mendispersikan polusi.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 7. BARIS 2 (2 CHART: TREN BULANAN & MUSIMAN)
# ==========================================
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown('<div class="chart-header">📈 3. Tren Rerata PM2.5 Bulanan</div>', unsafe_allow_html=True)
    monthly_pm25 = filtered_df.groupby('month')['PM2.5'].mean().reset_index()

    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    sns.lineplot(
        x='month', y='PM2.5', data=monthly_pm25,
        marker='o', color='#1F77B4', linewidth=2.5, markersize=7, ax=ax3
    )
    ax3.set_xlabel("Bulan ke-", fontsize=10)
    ax3.set_ylabel("Rerata PM2.5 (µg/m³)", fontsize=10)
    ax3.set_xticks(range(1, 13))
    ax3.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig3)

    st.markdown("""
        <div class="insight-box">
            💡 <b>Insight Fluktuasi Bulanan:</b> Polusi udara melonjak tinggi pada bulan <b>Desember, Januari, dan Maret</b>, serta menyentuh level paling bersih di pertengahan tahun (<b>Agustus</b>).
        </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown('<div class="chart-header">🍂 4. Rerata PM2.5 Berdasarkan Musim</div>', unsafe_allow_html=True)
    def assign_season(m):
        if m in [12, 1, 2]: return 'Winter'
        elif m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        else: return 'Autumn'

    filtered_df['season'] = filtered_df['month'].apply(assign_season)
    seasonal_pm25 = filtered_df.groupby('season')['PM2.5'].mean().reindex(['Spring', 'Summer', 'Autumn', 'Winter']).reset_index()

    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    sns.barplot(
        x='season', y='PM2.5', hue='season',
        data=seasonal_pm25, palette='YlOrRd', legend=False, ax=ax4
    )
    ax4.set_xlabel("Musim", fontsize=10)
    ax4.set_ylabel("Rerata PM2.5 (µg/m³)", fontsize=10)
    ax4.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig4)

    st.markdown("""
        <div class="insight-box">
            💡 <b>Insight Musiman:</b> <b>Musim Dingin (Winter)</b> mencatatkan rerata polusi paling ekstrem akibat pengoperasian pemanas ruangan berbasis batubara secara masif.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 8. BARIS 3 (2 CHART: BINNING AQI & POLA HARIAN/JAM-JAMAN)
# ==========================================
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.markdown('<div class="chart-header">🏷️ 5. Distribusi Kategori Kualitas Udara Harian</div>', unsafe_allow_html=True)
    
    def categorize_air_quality(val):
        if val <= 35: return 'Baik (Good)'
        elif val <= 75: return 'Sedang (Moderate)'
        elif val <= 115: return 'Tidak Sehat'
        else: return 'Sangat Tidak Sehat'

    filtered_df['air_quality_category'] = filtered_df['PM2.5'].apply(categorize_air_quality)
    cat_order = ['Baik (Good)', 'Sedang (Moderate)', 'Tidak Sehat', 'Sangat Tidak Sehat']
    colors_cat = ['#2E7D32', '#FBC02D', '#F57C00', '#D32F2F']

    fig5, ax5 = plt.subplots(figsize=(7, 4.5))
    sns.countplot(
        data=filtered_df, x='air_quality_category', order=cat_order,
        palette=colors_cat, hue='air_quality_category', legend=False, ax=ax5
    )

    total_count = len(filtered_df)
    for p in ax5.patches:
        height = p.get_height()
        if height > 0:
            percentage = f'{(height/total_count)*100:.1f}%'
            ax5.annotate(percentage, (p.get_x() + p.get_width() / 2., height + (total_count * 0.01)),
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax5.set_xlabel("Kategori Kualitas Udara", fontsize=10)
    ax5.set_ylabel("Jumlah Jam Observasi", fontsize=10)
    st.pyplot(fig5)

    st.markdown("""
        <div class="insight-box">
            💡 <b>Insight Kategori Udara:</b> Sebesar <b>39.1%</b> dari total durasi jam berada pada kualifikasi <i>Tidak Sehat</i> hingga <i>Sangat Tidak Sehat</i>, menandakan tingginya frekuensi lonjakan polusi.
        </div>
    """, unsafe_allow_html=True)

with row3_col2:
    st.markdown('<div class="chart-header">⏰ 6. Pola Fluktuasi PM2.5 Jam-jaman (Diurnal)</div>', unsafe_allow_html=True)
    hourly_pm25 = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

    fig6, ax6 = plt.subplots(figsize=(7, 4.5))
    sns.lineplot(
        x='hour', y='PM2.5', data=hourly_pm25,
        marker='o', color='#E65100', linewidth=2.5, markersize=6, ax=ax6
    )
    ax6.set_xlabel("Jam (00:00 - 23:00)", fontsize=10)
    ax6.set_ylabel("Rerata PM2.5 (µg/m³)", fontsize=10)
    ax6.set_xticks(range(0, 24, 2))
    ax6.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig6)

    st.markdown("""
        <div class="insight-box">
            💡 <b>Insight Pola Jam-jaman:</b> Konsentrasi polusi udara cenderung meningkat pesat pada <b>malam hingga dini hari (21:00 - 02:00)</b> akibat penurunan suhu udara dan inversi termal nocturnal.
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Proyek Analisis Data Dicoding | Air Quality Dataset Beijing | Dashboard Interaktif Streamlit")