import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import streamlit as st
from collections import Counter
import ast

# ── KONFIGURASI HALAMAN ──────────────────────────────────
st.set_page_config(
    page_title="Recipe Intelligence Dashboard",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS CUSTOM ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1923;
}
[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}
[data-testid="stSidebar"] .stRadio label {
    color: #e8e8e8 !important;
    font-size: 14px;
}

/* Header utama */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--text-color);
    line-height: 1.2;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    font-size: 1rem;
    color: var(--text-color);
    opacity: 0.7;
    margin-bottom: 1.5rem;
}

/* Metric cards */
.metric-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 4px solid #f97316;
}
.metric-card .label {
    font-size: 12px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}
.metric-card .value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a1a2e;
    line-height: 1;
}
.metric-card .sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 0.3rem;
}

/* Insight box */
.insight-box {
    background: #0f1923;
    color: #e8f4fd !important;
    padding: 14px 18px;
    border-radius: 10px;
    border-left: 5px solid #f97316;
    font-size: 14px;
    margin-top: 12px;
    line-height: 1.8;
}
.insight-box * { color: #e8f4fd !important; }
.insight-box b { color: #fb923c !important; }
.insight-box code {
    background: #1e3a5f;
    color: #fbbf24 !important;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
}

/* Section header */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: var(--text-color);
    border-bottom: 2px solid #f97316;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* Cluster badge */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/resep_bersih_clustered.csv")
    except FileNotFoundError:
        df = pd.read_csv("resep_bersih_clustered.csv")

    # Parse ingredients_list jika masih string
    if isinstance(df['ingredients_list'].iloc[0], str):
        try:
            df['ingredients_list'] = df['ingredients_list'].apply(ast.literal_eval)
        except Exception:
            df['ingredients_list'] = df['ingredients_list'].apply(lambda x: x.strip("[]").replace("'", "").split(", "))

    df['n_ingredients'] = df['ingredients_list'].apply(len)

    def kategori_diet(k):
        if k < 400:    return 'Rendah Kalori (<400 kkal)'
        elif k <= 800: return 'Normal (400-800 kkal)'
        else:          return 'Tinggi Kalori (>800 kkal)'

    df['kategori_diet'] = df['calories'].apply(kategori_diet)
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍳 Recipe Intelligence")
    st.markdown("---")

    st.markdown("### 🔍 Navigasi")
    page = st.radio(
        label="Pilih Halaman",
        options=[
            "📊 Overview Dataset",
            "🥕 Pertanyaan 1 — Bahan Populer",
            "🔥 Pertanyaan 2 — Penyebab Kalori Tinggi",
            "⏱️ Pertanyaan 3 — Batas Waktu Memasak",
            "🥗 Pertanyaan 4 — Diet vs Kompleksitas",
            "🤖 Pertanyaan 5 — Clustering Resep",
            "🧪 A/B Testing — Simulasi Strategi Resep",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### 🎛️ Filter Global")
    max_menit = st.slider("Maks. Waktu Memasak (menit)", 5, 300, 300, step=5)
    max_kalori = st.slider("Maks. Kalori (kkal)", 100, 3000, 3000, step=50)
    cluster_filter = st.multiselect(
        "Kategori Cluster",
        options=df['cluster_label'].unique().tolist(),
        default=df['cluster_label'].unique().tolist()
    )

    st.markdown("---")
    st.markdown('<small style="color:#6b7280">© 2025 Recipe Intelligence Dashboard</small>', unsafe_allow_html=True)

# Filter data berdasarkan sidebar
df_filtered = df[
    (df['minutes'] <= max_menit) &
    (df['calories'] <= max_kalori) &
    (df['cluster_label'].isin(cluster_filter))
]

# ══════════════════════════════════════════════════════════
# HALAMAN: OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "📊 Overview Dataset":
    st.markdown('<div class="hero-title">Recipe Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Analisis mendalam terhadap dataset resep makanan untuk mengurangi food waste dan membantu pengguna memasak lebih cerdas.</div>', unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Total Resep", f"{len(df_filtered):,}", "setelah filtering"),
        ("Rata-rata Kalori", f"{df_filtered['calories'].mean():.0f} kkal", "per resep"),
        ("Median Waktu Masak", f"{df_filtered['minutes'].median():.0f} menit", "per resep"),
        ("Rata-rata Bahan", f"{df_filtered['n_ingredients'].mean():.1f} bahan", "per resep"),
    ]
    colors = ["#f97316", "#3b82f6", "#10b981", "#8b5cf6"]
    for col, (label, value, sub), color in zip([col1, col2, col3, col4], metrics, colors):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color:{color}">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribusi cluster
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.markdown('<div class="section-header">Distribusi Kategori Resep</div>', unsafe_allow_html=True)
        cluster_dist = df_filtered['cluster_label'].value_counts().reset_index()
        cluster_dist.columns = ['Kategori', 'Jumlah']

        palette_map = {
            'Menu Diet (Rendah Kalori)':     '#10b981',
            'Tinggi Protein (Muscle Building)': '#3b82f6',
            'Tinggi Karbohidrat & Gula':     '#f59e0b',
            'Makanan Berat (Comfort Food)':  '#ef4444',
        }
        colors_bar = [palette_map.get(k, '#6b7280') for k in cluster_dist['Kategori']]

        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(cluster_dist['Kategori'], cluster_dist['Jumlah'],
                       color=colors_bar, height=0.55, edgecolor='white')
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 100, bar.get_y() + bar.get_height()/2,
                    f'{int(w):,} resep', va='center', fontsize=10, fontweight='bold', color='#374151')
        ax.set_xlabel('Jumlah Resep', fontsize=10)
        ax.set_xlim(0, cluster_dist['Jumlah'].max() * 1.2)
        ax.set_title('Komposisi Resep per Kategori Diet', fontsize=12, fontweight='bold', pad=10)
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown('<div class="section-header">Statistik Ringkas</div>', unsafe_allow_html=True)
        stat_data = df_filtered[['calories', 'total_fat', 'sugar', 'protein', 'carbs', 'minutes', 'n_ingredients']].describe().T[['mean', '50%', 'min', 'max']]
        stat_data.columns = ['Rata-rata', 'Median', 'Min', 'Maks']
        stat_data = stat_data.round(1)
        st.dataframe(stat_data, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        📌 <b>Konteks Dataset:</b><br>
        Dataset ini berisi resep dari platform Food.com yang telah dibersihkan dari outlier
        (waktu > 300 menit & kalori > 3000 kkal). Gunakan <b>filter di sidebar</b> untuk
        menyesuaikan analisis sesuai kebutuhan Anda.
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: PERTANYAAN 1 — BAHAN POPULER
# ══════════════════════════════════════════════════════════
elif page == "🥕 Pertanyaan 1 — Bahan Populer":
    st.markdown('<div class="hero-title">Pertanyaan 1 — WHAT</div>', unsafe_allow_html=True)
    st.markdown("**Apa saja bahan dasar yang paling sering digunakan dan wajib ada di dapur pengguna?**")
    st.markdown("---")

    top_n = st.select_slider("Tampilkan Top N Bahan", options=[5, 10, 15, 20], value=10)

    semua_bahan = [b for daftar in df_filtered['ingredients_list'] for b in daftar]
    hitung_bahan = Counter(semua_bahan)
    df_bahan = pd.DataFrame(hitung_bahan.most_common(top_n), columns=['Bahan', 'Frekuensi'])

    fig, ax = plt.subplots(figsize=(10, 6))
    palette = sns.color_palette("YlOrRd", n_colors=top_n)[::-1]
    bars = ax.barh(df_bahan['Bahan'][::-1], df_bahan['Frekuensi'][::-1],
                   color=palette, height=0.6, edgecolor='white')

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 150, bar.get_y() + bar.get_height()/2,
                f'{int(w):,}x', va='center', fontsize=10, fontweight='bold', color='#374151')

    ax.set_title(f'Top {top_n} Bahan Makanan Paling Sering Digunakan', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Jumlah Kemunculan dalam Dataset', fontsize=11)
    ax.set_ylabel('Nama Bahan', fontsize=11)
    ax.set_xlim(0, df_bahan['Frekuensi'].max() * 1.18)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Rangkuman Pertanyaan 1 (WHAT):</b><br>
    • <b>Salt (garam)</b> mendominasi sebagai bahan paling sering muncul, disusul <b>butter</b> dan <b>sugar</b> — ketiganya hadir di hampir setiap kategori masakan.<br>
    • Bahan seperti <b>eggs, flour, garlic, onion</b> juga masuk Top 10, mencerminkan dominasi resep berbasis masakan Barat dalam dataset.<br>
    • <b>Insight Bisnis:</b> Bahan-bahan Top {top_n} ini dapat dijadikan <b>Pantry Essentials</b> (bahan default) di aplikasi — pengguna tidak perlu menginput ulang bahan dasar setiap kali mencari resep.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: PERTANYAAN 2 — PENYEBAB KALORI TINGGI
# ══════════════════════════════════════════════════════════
elif page == "🔥 Pertanyaan 2 — Penyebab Kalori Tinggi":
    st.markdown('<div class="hero-title">Pertanyaan 2 — WHY</div>', unsafe_allow_html=True)
    st.markdown("**Mengapa sebuah resep bisa memiliki kalori yang sangat tinggi? Komponen nutrisi apa penyebab utamanya?**")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1.4])

    with col_left:
        st.markdown('<div class="section-header">Heatmap Korelasi Nutrisi</div>', unsafe_allow_html=True)

        korelasi = df_filtered[['calories', 'total_fat', 'sugar', 'carbs', 'protein']].corr()
        korelasi_kalori = korelasi[['calories']].sort_values(by='calories', ascending=False).drop('calories')

        fig, ax = plt.subplots(figsize=(4.5, 5.5))
        sns.heatmap(korelasi_kalori, annot=True, cmap='YlOrRd', vmin=0, vmax=1,
                    annot_kws={"size": 16, "weight": "bold"}, fmt=".2f",
                    linewidths=1.5, linecolor='white', ax=ax,
                    cbar_kws={"label": "Koefisien Korelasi"})
        ax.set_title('Korelasi Makronutrisi\nterhadap Kalori', fontsize=12, fontweight='bold', pad=12)
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.tick_params(axis='y', labelsize=11, rotation=0)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.markdown('<div class="section-header">Perbandingan Kekuatan Korelasi</div>', unsafe_allow_html=True)

        korelasi_vals = korelasi['calories'].drop('calories').sort_values(ascending=True)
        colors_corr = ['#ef4444' if v >= 0.7 else '#f59e0b' if v >= 0.4 else '#10b981' for v in korelasi_vals]

        fig, ax = plt.subplots(figsize=(7, 4.5))
        bars = ax.barh(korelasi_vals.index, korelasi_vals.values, color=colors_corr, height=0.5, edgecolor='white')

        for bar, val in zip(bars, korelasi_vals.values):
            ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                    f'r = {val:.2f}', va='center', fontsize=11, fontweight='bold')

        ax.axvline(x=0.7, color='#ef4444', linestyle='--', linewidth=1.2, alpha=0.5)
        ax.text(0.71, -0.5, 'Korelasi Kuat', color='#ef4444', fontsize=8)
        ax.set_xlabel('Koefisien Korelasi Pearson (r)', fontsize=11)
        ax.set_title('Seberapa Kuat Tiap Nutrisi\nMemengaruhi Kalori?', fontsize=12, fontweight='bold', pad=12)
        ax.set_xlim(0, 1.15)
        patches = [
            mpatches.Patch(color='#ef4444', label='Korelasi Kuat (r >= 0.7)'),
            mpatches.Patch(color='#f59e0b', label='Korelasi Sedang (r >= 0.4)'),
            mpatches.Patch(color='#10b981', label='Korelasi Lemah (r < 0.4)'),
        ]
        ax.legend(handles=patches, fontsize=8, loc='lower right')
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("""
    <div class="insight-box">
    📌 <b>Rangkuman Pertanyaan 2 (WHY):</b><br>
    • <b>Total Fat (Lemak)</b> adalah penyumbang kalori terbesar dengan korelasi tertinggi (r ~ 0.90) — jauh melampaui komponen lainnya.<br>
    • <b>Carbs</b> dan <b>Sugar</b> berada di posisi kedua dan ketiga, sementara <b>Protein</b> memiliki kontribusi terendah terhadap total kalori.<br>
    • <b>Insight Bisnis:</b> Sistem filter aplikasi harus memprioritaskan pemotongan resep berlemak tinggi (<code>total_fat</code>) jika pengguna memilih mode <b>Rendah Kalori</b>.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: PERTANYAAN 3 — BATAS WAKTU
# ══════════════════════════════════════════════════════════
elif page == "⏱️ Pertanyaan 3 — Batas Waktu Memasak":
    st.markdown('<div class="hero-title">Pertanyaan 3 — WHEN</div>', unsafe_allow_html=True)
    st.markdown("**Berapa batas waktu memasak maksimal sebelum pengguna merasa malas dan membiarkan bahan makanannya membusuk?**")
    st.markdown("---")

    threshold = st.slider("Atur Threshold Waktu (menit)", min_value=15, max_value=120, value=45, step=5)
    pct_bawah = (df_filtered['minutes'] <= threshold).mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Resep di bawah threshold", f"{pct_bawah:.1f}%", f"<= {threshold} menit")
    col2.metric("Median Waktu Memasak", f"{df_filtered['minutes'].median():.0f} menit")
    col3.metric("Resep Tercepat", f"{df_filtered['minutes'].min()} menit")

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.histplot(df_filtered['minutes'], bins=60, kde=True, color='#3b82f6',
                 edgecolor='white', alpha=0.8, ax=ax)

    ax.axvline(x=threshold, color='#f97316', linestyle='--', linewidth=2.5,
               label=f'Threshold: {threshold} menit ({pct_bawah:.1f}% resep di bawah ini)')

    ymax = ax.get_ylim()[1]
    ax.fill_betweenx([0, ymax], 0, threshold, color='#10b981', alpha=0.07, label='Zona Nyaman Memasak')
    ax.fill_betweenx([0, ymax], threshold, 150, color='#ef4444', alpha=0.05, label='Zona Risiko Food Waste')

    ax.text(threshold * 0.45, ymax * 0.8, f'{pct_bawah:.1f}%\nResep Cepat',
            ha='center', fontsize=13, fontweight='bold', color='#10b981')
    ax.text(threshold + (150 - threshold) * 0.45, ymax * 0.8, f'{100 - pct_bawah:.1f}%\nResep Lambat',
            ha='center', fontsize=13, fontweight='bold', color='#ef4444')

    ax.set_title(f'WHEN: Distribusi Waktu Memasak & Threshold {threshold} Menit',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Waktu Memasak (Menit)', fontsize=12)
    ax.set_ylabel('Frekuensi (Jumlah Resep)', fontsize=12)
    ax.set_xlim(0, 150)
    ax.legend(fontsize=10)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Rangkuman Pertanyaan 3 (WHEN):</b><br>
    • Distribusi waktu memasak membentuk kurva <b>right-skewed</b>, dengan puncak tertinggi di rentang <b>15–45 menit</b>.<br>
    • Berdasarkan pola distribusi dataset, threshold <b>{threshold} menit</b> ditetapkan sebagai batas waktu yang realistis —
      <b>{pct_bawah:.1f}%</b> resep berada di bawah batas ini, menunjukkan bahwa pengguna secara alami cenderung memilih resep yang dapat diselesaikan dalam rentang waktu tersebut.<br>
    • Resep yang membutuhkan waktu lebih dari {threshold} menit memiliki frekuensi yang jauh menurun, mengindikasikan semakin lama waktu memasak, semakin sedikit resep yang dipilih pengguna.<br>
    • <b>Insight Bisnis:</b> Aplikasi akan <b>memprioritaskan resep <= {threshold} menit</b> di halaman utama. Resep di atas batas ini akan diberi label <b>'Butuh Waktu Ekstra'</b> agar pengguna dapat membuat keputusan yang lebih tepat dan bahan di kulkas tidak terbuang sia-sia.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: PERTANYAAN 4 — DIET VS KOMPLEKSITAS
# ══════════════════════════════════════════════════════════
elif page == "🥗 Pertanyaan 4 — Diet vs Kompleksitas":
    st.markdown('<div class="hero-title">Pertanyaan 4 — WHO</div>', unsafe_allow_html=True)
    st.markdown("**Siapa yang akan sangat diuntungkan dari resep yang rendah kalori namun prosesnya tidak ribet?**")
    st.markdown("---")

    order   = ['Rendah Kalori (<400 kkal)', 'Normal (400-800 kkal)', 'Tinggi Kalori (>800 kkal)']
    palette = ['#10b981', '#f59e0b', '#ef4444']

    df_cat = df_filtered[df_filtered['kategori_diet'].isin(order)]
    stats  = df_cat.groupby('kategori_diet')['n_ingredients'].agg(['median', 'mean', 'count']).reset_index()
    stats.columns = ['Kategori', 'Median', 'Mean', 'Jumlah']
    stats['Kategori_urut'] = pd.Categorical(stats['Kategori'], categories=order, ordered=True)
    stats = stats.sort_values('Kategori_urut')

    col_chart, col_info = st.columns([1.6, 1])

    with col_chart:
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(
            stats['Kategori'], stats['Median'],
            color=palette, width=0.45, edgecolor='white', linewidth=1.5
        )
        for bar, row in zip(bars, stats.itertuples()):
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.12,
                    f'{int(h)} bahan', ha='center', va='bottom',
                    fontsize=13, fontweight='bold', color='#1a1a2e')
            ax.text(bar.get_x() + bar.get_width()/2., h/2,
                    f'n={row.Jumlah:,}', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')

        ax.axhline(y=10, color='#6b7280', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(2.27, 10.15, 'Batas "Simpel": 10 bahan', color='#6b7280', fontsize=9, va='bottom')

        ax.set_title('WHO: Resep Sehat Terbukti Lebih Sederhana\nMedian Jumlah Bahan per Kategori Kalori',
                     fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Kategori Resep', fontsize=11)
        ax.set_ylabel('Median Jumlah Bahan', fontsize=11)
        ax.set_ylim(0, stats['Median'].max() + 3.5)
        ax.set_xticklabels(stats['Kategori'], fontsize=10)
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_info:
        st.markdown('<div class="section-header">Profil Tiap Kategori</div>', unsafe_allow_html=True)
        icons = ['🥗', '🍽️', '🍔']
        descs = [
            "Ideal untuk diet, anak kos, dan pekerja sibuk. Bahan sedikit, mudah disiapkan.",
            "Resep sehari-hari. Keseimbangan antara rasa dan nutrisi.",
            "Comfort food & resep kompleks. Butuh lebih banyak bahan dan persiapan."
        ]
        for icon, row, desc, color in zip(icons, stats.itertuples(), descs, palette):
            st.markdown(f"""
            <div style="background:#f9fafb;border-left:4px solid {color};
                        border-radius:8px;padding:12px 14px;margin-bottom:10px;">
                <div style="font-size:1.1rem;font-weight:700;color:#1a1a2e">{icon} {row.Kategori.split('(')[0].strip()}</div>
                <div style="font-size:1.6rem;font-weight:700;color:{color}">Median {int(row.Median)} bahan</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    📌 <b>Rangkuman Pertanyaan 4 (WHO):</b><br>
    • Resep <b>Rendah Kalori</b> memiliki <b>median jumlah bahan paling sedikit</b>, mematahkan mitos bahwa makanan sehat itu ribet dan memerlukan banyak bahan.<br>
    • Sebaliknya, kategori <b>Tinggi Kalori</b> cenderung memerlukan lebih banyak bahan — lebih kompleks dan membutuhkan lebih banyak persiapan.<br>
    • <b>Insight Bisnis:</b> Fitur <b>'Resep Sehat & Simpel'</b> (filter: kalori < 400 & bahan <= 10) dapat menjadi fitur unggulan aplikasi untuk mengurangi food waste pada pengguna dengan keterbatasan bahan.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: PERTANYAAN 5 — CLUSTERING
# ══════════════════════════════════════════════════════════
elif page == "🤖 Pertanyaan 5 — Clustering Resep":
    st.markdown('<div class="hero-title">Pertanyaan 5 — HOW</div>', unsafe_allow_html=True)
    st.markdown("**Bagaimana cara sistem mengelompokkan puluhan ribu resep secara otomatis agar pengguna mudah memilih jenis dietnya?**")
    st.markdown("---")

    palette_map = {
        'Menu Diet (Rendah Kalori)':        '#10b981',
        'Tinggi Protein (Muscle Building)': '#3b82f6',
        'Tinggi Karbohidrat & Gula':        '#f59e0b',
        'Makanan Berat (Comfort Food)':     '#ef4444',
    }
    icon_map = {
        'Menu Diet (Rendah Kalori)':        '🥗',
        'Tinggi Protein (Muscle Building)': '💪',
        'Tinggi Karbohidrat & Gula':        '🍰',
        'Makanan Berat (Comfort Food)':     '🍔',
    }

    # Profil cluster
    fitur = ['calories', 'total_fat', 'sugar', 'protein', 'carbs']
    profil = df_filtered.groupby('cluster_label')[fitur + ['n_ingredients', 'minutes']].mean().round(1)

    col_bar, col_radar = st.columns([1.2, 1])

    with col_bar:
        st.markdown('<div class="section-header">Rata-rata Kalori per Cluster</div>', unsafe_allow_html=True)
        kalori_avg = df_filtered.groupby('cluster_label')['calories'].mean().reset_index()
        kalori_avg = kalori_avg.sort_values('calories')
        colors_bar = [palette_map.get(k, '#6b7280') for k in kalori_avg['cluster_label']]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(kalori_avg['cluster_label'], kalori_avg['calories'],
                       color=colors_bar, height=0.5, edgecolor='white')
        for bar, (_, row) in zip(bars, kalori_avg.iterrows()):
            w = bar.get_width()
            ax.text(w + 10, bar.get_y() + bar.get_height()/2,
                    f'{w:.0f} kkal', va='center', fontsize=11, fontweight='bold', color='#374151')
        ax.set_xlabel('Rata-rata Kalori per Porsi (kkal)', fontsize=11)
        ax.set_xlim(0, kalori_avg['calories'].max() * 1.25)
        ax.set_title('HOW: Perbandingan Rata-rata Kalori\nper Kategori Cluster', fontsize=12, fontweight='bold', pad=12)
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_radar:
        st.markdown('<div class="section-header">Profil Nutrisi per Cluster</div>', unsafe_allow_html=True)
        for label, row in profil.iterrows():
            color  = palette_map.get(label, '#6b7280')
            icon   = icon_map.get(label, '🍽️')
            count  = len(df_filtered[df_filtered['cluster_label'] == label])
            st.markdown(f"""
            <div style="background:#f9fafb;border-left:4px solid {color};
                        border-radius:8px;padding:10px 14px;margin-bottom:8px;">
                <div style="font-weight:700;color:#1a1a2e;font-size:14px">{icon} {label}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">
                    {count:,} resep &nbsp;|&nbsp;
                    🔥 {row['calories']:.0f} kkal &nbsp;|&nbsp;
                    🥩 Protein {row['protein']:.0f} &nbsp;|&nbsp;
                    🧈 Fat {row['total_fat']:.0f} &nbsp;|&nbsp;
                    🍞 Carbs {row['carbs']:.0f}
                </div>
            </div>""", unsafe_allow_html=True)

    # Tabel sampel resep per cluster
    st.markdown('<div class="section-header" style="margin-top:1.5rem">Eksplorasi Resep per Kategori</div>', unsafe_allow_html=True)
    selected_cluster = st.selectbox("Pilih Kategori:", options=list(palette_map.keys()))
    n_show = st.slider("Tampilkan berapa resep?", 5, 30, 10)

    df_sample = df_filtered[df_filtered['cluster_label'] == selected_cluster][
        ['name', 'minutes', 'n_ingredients', 'calories', 'protein', 'total_fat', 'carbs']
    ].sort_values('calories').head(n_show).reset_index(drop=True)

    df_sample.columns = ['Nama Resep', 'Waktu (mnt)', 'Jml Bahan', 'Kalori', 'Protein', 'Lemak', 'Karbo']
    st.dataframe(df_sample, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Rangkuman Pertanyaan 5 (HOW):</b><br>
    • K-Means Clustering berhasil memisahkan resep ke dalam <b>4 kategori</b> dengan profil nutrisi yang berbeda secara signifikan.<br>
    • <b>Elbow Method</b> mengonfirmasi bahwa 4 cluster adalah jumlah optimal berdasarkan titik siku pada kurva distortion score.<br>
    • <b>4 Kategori:</b> 🥗 Menu Diet — 💪 Tinggi Protein — 🍰 Tinggi Karbo & Gula — 🍔 Makanan Berat.<br>
    • <b>Insight Bisnis:</b> Hasil clustering ini langsung diimplementasikan sebagai fitur <b>Filter Preferensi Diet</b> — pengguna cukup memilih 1 kategori dan sistem otomatis menyaring ribuan resep yang relevan.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: A/B TESTING
# ══════════════════════════════════════════════════════════
elif page == "🧪 A/B Testing — Simulasi Strategi Resep":
    st.markdown('<div class="hero-title">A/B Testing — Simulasi Strategi Resep</div>', unsafe_allow_html=True)
    st.markdown("Bandingkan dua strategi filter resep secara head-to-head untuk menentukan mana yang lebih efektif mengurangi food waste dan meningkatkan kepuasan pengguna.")
    st.markdown("---")

    # ── KONFIGURASI GRUP A & B ───────────────────────────
    st.markdown('<div class="section-header">⚙️ Konfigurasi Eksperimen</div>', unsafe_allow_html=True)

    col_a, col_vs, col_b = st.columns([5, 1, 5])

    with col_a:
        st.markdown("""
        <div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:12px;
                    padding:16px;text-align:center;margin-bottom:12px">
            <span style="font-size:1.5rem;font-weight:700;color:#1d4ed8">🅰️ Grup A</span><br>
            <span style="font-size:12px;color:#6b7280">Strategi Kontrol (Baseline)</span>
        </div>""", unsafe_allow_html=True)

        a_max_menit  = st.slider("Maks. Waktu Masak", 10, 300, 45,  step=5,  key="a_menit",  help="Filter resep berdasarkan durasi memasak")
        a_max_kalori = st.slider("Maks. Kalori",      100, 3000, 800, step=50, key="a_kalori", help="Filter resep berdasarkan kandungan kalori")
        a_max_bahan  = st.slider("Maks. Jumlah Bahan", 2,  30,   10,  step=1,  key="a_bahan",  help="Filter resep berdasarkan jumlah bahan")
        a_cluster    = st.multiselect(
            "Kategori Cluster",
            options=df['cluster_label'].unique().tolist(),
            default=['Menu Diet (Rendah Kalori)', 'Tinggi Protein (Muscle Building)'],
            key="a_cluster"
        )

    with col_vs:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;font-size:1.8rem;font-weight:900;
                    color:#6b7280;padding-top:60px">VS</div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div style="background:#fef3c7;border:2px solid #f59e0b;border-radius:12px;
                    padding:16px;text-align:center;margin-bottom:12px">
            <span style="font-size:1.5rem;font-weight:700;color:#b45309">🅱️ Grup B</span><br>
            <span style="font-size:12px;color:#6b7280">Strategi Challenger</span>
        </div>""", unsafe_allow_html=True)

        b_max_menit  = st.slider("Maks. Waktu Masak", 10, 300, 90,  step=5,  key="b_menit")
        b_max_kalori = st.slider("Maks. Kalori",      100, 3000, 1200, step=50, key="b_kalori")
        b_max_bahan  = st.slider("Maks. Jumlah Bahan", 2,  30,   15,  step=1,  key="b_bahan")
        b_cluster    = st.multiselect(
            "Kategori Cluster",
            options=df['cluster_label'].unique().tolist(),
            default=['Tinggi Karbohidrat & Gula', 'Makanan Berat (Comfort Food)'],
            key="b_cluster"
        )

    # ── FILTER DATA ──────────────────────────────────────
    df_a = df[
        (df['minutes']      <= a_max_menit)  &
        (df['calories']     <= a_max_kalori) &
        (df['n_ingredients'] <= a_max_bahan)  &
        (df['cluster_label'].isin(a_cluster))
    ]
    df_b = df[
        (df['minutes']      <= b_max_menit)  &
        (df['calories']     <= b_max_kalori) &
        (df['n_ingredients'] <= b_max_bahan)  &
        (df['cluster_label'].isin(b_cluster))
    ]

    st.markdown("---")

    # ── SCORECARD ────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Hasil Perbandingan</div>', unsafe_allow_html=True)

    metrics_config = [
        ("Total Resep Tersedia",    len(df_a),                       len(df_b),                       "",        "Lebih banyak pilihan = lebih baik"),
        ("Rata-rata Kalori",        df_a['calories'].mean(),         df_b['calories'].mean(),         " kkal",   "Lebih rendah = lebih sehat"),
        ("Median Waktu Masak",      df_a['minutes'].median(),        df_b['minutes'].median(),        " menit",  "Lebih cepat = risiko food waste lebih rendah"),
        ("Rata-rata Jumlah Bahan",  df_a['n_ingredients'].mean(),    df_b['n_ingredients'].mean(),    " bahan",  "Lebih sedikit = lebih simpel"),
        ("Rata-rata Protein",       df_a['protein'].mean(),          df_b['protein'].mean(),          "",        "Lebih tinggi = lebih bergizi"),
        ("Rata-rata Lemak",         df_a['total_fat'].mean(),        df_b['total_fat'].mean(),        "",        "Lebih rendah = lebih sehat"),
    ]

    for label, val_a, val_b, suffix, tip in metrics_config:
        c1, c2, c3 = st.columns([3, 3, 4])
        # Tentukan pemenang per metrik
        if label in ["Rata-rata Kalori", "Median Waktu Masak", "Rata-rata Jumlah Bahan", "Rata-rata Lemak"]:
            a_wins = val_a < val_b
        else:
            a_wins = val_a > val_b

        badge_a = "✅" if a_wins     else "❌"
        badge_b = "✅" if not a_wins else "❌"
        color_a = "#eff6ff" if a_wins     else "#fff1f2"
        color_b = "#fef3c7" if not a_wins else "#fff1f2"
        border_a = "#3b82f6" if a_wins    else "#fca5a5"
        border_b = "#f59e0b" if not a_wins else "#fca5a5"

        try:
            fmt_a = f"{val_a:,.1f}{suffix}" if isinstance(val_a, float) else f"{val_a:,}{suffix}"
            fmt_b = f"{val_b:,.1f}{suffix}" if isinstance(val_b, float) else f"{val_b:,}{suffix}"
        except Exception:
            fmt_a, fmt_b = str(val_a), str(val_b)

        with c1:
            st.markdown(f"""
            <div style="background:{color_a};border:1.5px solid {border_a};border-radius:10px;
                        padding:10px 14px;text-align:center;margin-bottom:6px">
                <div style="font-size:11px;color:#6b7280;font-weight:600">🅰️ Grup A</div>
                <div style="font-size:1.4rem;font-weight:700;color:#1a1a2e">{badge_a} {fmt_a}</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="background:{color_b};border:1.5px solid {border_b};border-radius:10px;
                        padding:10px 14px;text-align:center;margin-bottom:6px">
                <div style="font-size:11px;color:#6b7280;font-weight:600">🅱️ Grup B</div>
                <div style="font-size:1.4rem;font-weight:700;color:#1a1a2e">{badge_b} {fmt_b}</div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="padding:10px 0 6px 4px">
                <div style="font-weight:600;color:var(--text-color);font-size:14px">{label}</div>
                <div style="font-size:12px;color:var(--text-color);opacity:0.7">{tip}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── GRAFIK PERBANDINGAN NUTRISI ───────────────────────
    st.markdown('<div class="section-header">📈 Perbandingan Profil Nutrisi</div>', unsafe_allow_html=True)

    nutrisi_labels = ['Kalori', 'Lemak', 'Gula', 'Protein', 'Karbo']
    nutrisi_cols   = ['calories', 'total_fat', 'sugar', 'protein', 'carbs']

    mean_a = [df_a[c].mean() for c in nutrisi_cols]
    mean_b = [df_b[c].mean() for c in nutrisi_cols]

    x     = np.arange(len(nutrisi_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    bars_a = ax.bar(x - width/2, mean_a, width, label='🅰️ Grup A', color='#3b82f6', edgecolor='white', linewidth=1.2)
    bars_b = ax.bar(x + width/2, mean_b, width, label='🅱️ Grup B', color='#f59e0b', edgecolor='white', linewidth=1.2)

    for bar in bars_a:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 1,
                f'{h:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1d4ed8')
    for bar in bars_b:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 1,
                f'{h:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#b45309')

    ax.set_title('Perbandingan Rata-rata Profil Nutrisi: Grup A vs Grup B',
                 fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(nutrisi_labels, fontsize=11)
    ax.set_ylabel('Nilai Rata-rata', fontsize=11)
    ax.legend(fontsize=11)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── DISTRIBUSI WAKTU MASAK A vs B ─────────────────────
    st.markdown('<div class="section-header">⏱️ Distribusi Waktu Memasak: A vs B</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.hist(df_a['minutes'], bins=40, alpha=0.6, color='#3b82f6', label=f'🅰️ Grup A (n={len(df_a):,})', edgecolor='white')
    ax.hist(df_b['minutes'], bins=40, alpha=0.6, color='#f59e0b', label=f'🅱️ Grup B (n={len(df_b):,})', edgecolor='white')
    ax.axvline(df_a['minutes'].median(), color='#1d4ed8', linestyle='--', linewidth=2,
               label=f'Median A: {df_a["minutes"].median():.0f} mnt')
    ax.axvline(df_b['minutes'].median(), color='#b45309', linestyle='--', linewidth=2,
               label=f'Median B: {df_b["minutes"].median():.0f} mnt')
    ax.set_xlabel('Waktu Memasak (Menit)', fontsize=11)
    ax.set_ylabel('Frekuensi', fontsize=11)
    ax.set_title('Distribusi Waktu Memasak: Grup A vs Grup B', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── KESIMPULAN A/B ────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏆 Kesimpulan A/B Testing</div>', unsafe_allow_html=True)

    score_a, score_b = 0, 0
    for label, val_a, val_b, _, _ in metrics_config:
        if label in ["Rata-rata Kalori", "Median Waktu Masak", "Rata-rata Jumlah Bahan", "Rata-rata Lemak"]:
            if val_a < val_b: score_a += 1
            else: score_b += 1
        else:
            if val_a > val_b: score_a += 1
            else: score_b += 1

    winner    = "🅰️ Grup A" if score_a >= score_b else "🅱️ Grup B"
    win_color = "#eff6ff"   if score_a >= score_b else "#fef3c7"
    win_border = "#3b82f6"  if score_a >= score_b else "#f59e0b"

    st.markdown(f"""
    <div style="background:{win_color};border:2px solid {win_border};border-radius:14px;
                padding:20px 24px;text-align:center;margin-bottom:16px">
        <div style="font-size:1rem;color:#6b7280;margin-bottom:4px">Pemenang Eksperimen</div>
        <div style="font-size:2rem;font-weight:700;color:#1a1a2e">{winner}</div>
        <div style="font-size:14px;color:#6b7280;margin-top:6px">
            Skor: <b>Grup A {score_a}</b> — <b>Grup B {score_b}</b> dari {len(metrics_config)} metrik
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
    📌 <b>Interpretasi Hasil A/B Testing:</b><br>
    • <b>Grup A</b> menggunakan filter lebih ketat (maks. {a_max_menit} mnt, {a_max_kalori} kkal, {a_max_bahan} bahan) — menghasilkan resep yang lebih sehat dan cepat namun pilihan lebih terbatas.<br>
    • <b>Grup B</b> menggunakan filter lebih longgar (maks. {b_max_menit} mnt, {b_max_kalori} kkal, {b_max_bahan} bahan) — menghasilkan lebih banyak variasi resep namun profil nutrisi cenderung lebih tinggi.<br>
    • <b>Pemenang ({winner})</b> unggul di <b>{max(score_a, score_b)}</b> dari {len(metrics_config)} metrik yang dibandingkan.<br>
    • <b>Rekomendasi:</b> Gunakan konfigurasi pemenang sebagai <b>default filter</b> aplikasi, dengan opsi bagi pengguna untuk beralih ke strategi lainnya sesuai preferensi pribadi.
    </div>""", unsafe_allow_html=True)