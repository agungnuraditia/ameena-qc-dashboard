import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import datetime
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard Prediksi NG",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOAD MODEL
# =====================================================

try:
    model = joblib.load("web-ng-prediction/model_rf.pkl")
except Exception as e:
    import streamlit as st
    st.error(f"🚨 GAGAL MEMUAT MODEL ASLI: {e}")
    # -----------------------------
    
    class DummyModel:
        def predict(self, df):
            if df["tipe_barang"].values[0] == "Hijab Maurin":
                return [4] 
            return [0] 
        def predict_proba(self, df):
            if df["tipe_barang"].values[0] == "Hijab Maurin":
                return [[0.05, 0.10, 0.05, 0.15, 0.60, 0.05]]
            return [[0.85, 0.03, 0.02, 0.05, 0.03, 0.02]]
    model = DummyModel()
# =====================================================
# FUNCTION
# =====================================================

def decode_prediction(pred):
    mapping = {
        0: "GOOD",
        1: "NG_JAHIT_LONCAT",
        2: "NG_NODA",
        3: "NG_PUCKER",
        4: "NG_ROBEK",
        5: "NG_TEPI_TIDAK_RAPI"
    }
    return mapping.get(pred, str(pred))

def get_download_data(df):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Riwayat Prediksi')
        return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    except Exception:
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Riwayat Prediksi')
            return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        except Exception:
            csv_data = df.to_csv(index=False).encode('utf-8')
            return csv_data, "csv", "text/csv"

# =====================================================
# INITIALIZE SESSION STATE FOR ACTIVE HISTORY
# =====================================================
import os

HISTORY_FILE = "history_data.csv"

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        return pd.DataFrame(columns=["Waktu", "Tipe Barang", "Operator", "Prediksi"])

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

# Selalu baca dari file CSV setiap kali web diakses (lewat komputer / HP)
st.session_state.history = load_history()

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #F8FAFC;
}

.block-container {
    padding-top: 3rem !important;
    padding-bottom: 2rem !important;
}

/* =====================================================
   SIDEBAR STYLE
   ===================================================== */
[data-testid="stSidebar"] {
    background-color: #0B1120 !important;
    border-right: none !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
}

[data-testid="stSidebar"] hr {
    border-color: #1E293B !important;
    margin-top: 25px !important;
    margin-bottom: 25px !important;
}

/* Logo Bebas Bingkai */
[data-testid="stSidebar"] [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 30px auto 10px auto !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stImage"] img {
    border-radius: 0 !important;
}

/* Style Menu Navigasi Modern Dark */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px !important;
}

/* Sembunyikan lingkaran bulat radio standar */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Memaksa font navigasi menjadi putih sepenuhnya */
[data-testid="stSidebar"] div[role="radiogroup"] > label,
[data-testid="stSidebar"] div[role="radiogroup"] > label p,
[data-testid="stSidebar"] div[role="radiogroup"] > label span {
    color: #FFFFFF !important; 
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background-color: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 18px !important;
    margin-bottom: 2px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #1E293B !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #1E293B !important;
    box-shadow: inset 0 0 0 1px #334155, 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p,
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] span {
    font-weight: 700 !important;
}

/* Kotak Informasi Bawah (Quality Intelligence) - DIBESARKAN */
.sidebar-info-box {
    background: #0F172A;
    border: 1px solid #1E293B;
    padding: 22px;
    border-radius: 14px;
    font-size: 13.5px; /* Lebih besar dari 11.5px */
    line-height: 1.7; /* Line height agar lega */
    color: #CBD5E1; /* Warna abu-abu terang agar sangat mudah dibaca */
    margin-top: 10px;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1);
}
.sidebar-info-box strong {
    color: #FFFFFF;
    font-size: 15px; /* Judul lebih besar */
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    letter-spacing: 0.05em;
}
.sidebar-info-box strong::before {
    content: "🔵";
    margin-right: 6px;
    font-size: 11px;
}
.status-badge {
    display: inline-block;
    background: #064E3B;
    color: #34D399;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.05em;
}

/* =====================================================
   MAIN AREA STYLE
   ===================================================== */
h1, h2, h3, h4, h5 {
    color: #0F172A;
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
}

.title-dashboard {
    font-size: 34px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.3;
    margin-top: 5px;
    margin-bottom: 6px;
    font-family: 'Outfit', sans-serif;
    letter-spacing: -0.02em;
}

.sub-dashboard {
    font-size: 15px;
    color: #64748B;
    margin-bottom: 35px;
    line-height: 1.5;
}

div[data-testid="stVerticalBlockBordered"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 22px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.02) !important;
}

.stButton>button {
    background: #0F172A !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    height: 48px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15) !important;
    transition: all 0.2s ease !important;
    font-family: 'Outfit', sans-serif !important;
}

.stButton>button:hover {
    background: #1E3A8A !important;
    box-shadow: 0 6px 14px rgba(30, 58, 138, 0.25) !important;
    transform: translateY(-1px) !important;
    color: white !important;
}

.prediction-box {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
    border: 1px solid #E2E8F0;
    text-align: center;
}

[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
}

.stDownloadButton>button {
    background: #0F172A !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    height: 42px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 6px rgba(15, 23, 42, 0.1) !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton>button:hover {
    background: #1E3A8A !important;
    box-shadow: 0 6px 12px rgba(30, 58, 138, 0.2) !important;
    transform: translateY(-1px) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR CONTENT
# =====================================================

# Ukuran logo dinaikkan secara drastis
import os

logo_path = os.path.join("assets", "logo.png")
# st.sidebar.image(logo_path, width=145)
# Teks AMEENA BABY & KIDS STORE
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 5px; margin-bottom: 35px;">
    <h1 style="font-size: 18px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.05em; margin: 0; font-family: 'Outfit', sans-serif; line-height: 1.4;">
        AMEENA<br>BABY & KIDS STORE
    </h1>
</div>
<div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.1em; margin-bottom:12px; margin-left:12px;">SISTEM UTAMA</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasi Utama", ["🖥️ Prediksi NG", "ℹ️ Tentang Sistem"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-info-box">
    <strong>QUALITY INTELLIGENCE</strong>
    Pantau anomali produksi secara presisi melalui mesin pembelajaran saraf Random Forest.
    <div style="display:flex; justify-content: space-between; align-items:center; margin-top: 25px;">
        <span style="font-size:11.5px; color:#94A3B8; font-weight:700; letter-spacing:0.1em;">STATUS</span>
        <span class="status-badge">● OPERATIONAL</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# MAIN PAGE ROUTING
# =====================================================

if menu == "🖥️ Prediksi NG":

    st.markdown('<div class="title-dashboard">Dashboard Prediksi NG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-dashboard">Sistem Prediksi Not Good (NG) Produksi Kerudung Anak</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1], gap="large")

    # =====================================================
    # INPUT PANEL
    # =====================================================
    with left_col:
        with st.container(border=True):
            st.subheader("📥 Input Data Produksi")
            st.markdown("<p style='color: #64748B; font-size: 13.5px; margin-top: -8px; margin-bottom: 20px;'>Masukkan detail produk di bawah ini untuk memprediksi kualitas hasil akhir</p>", unsafe_allow_html=True)

            tipe_barang = st.selectbox("Tipe Barang", [
                "Hijab Arafa", "Hijab Bella Pita", "Hijab Carla", "Hijab Dagu Malay", "Hijab Dinda", 
                "Hijab Kancing Ziya", "Hijab Maurin", "Hijab Pashmina Instan | Zanaya", 
                "Hijab Raina", "Hijab Sakura", "Hijab Shafana", "Hijab Sport Aleeya"
            ])

            warna_kain = st.selectbox("Warna Kain", [
                "Abu", "Blush Red", "Burgundi", "Coffee", "Coksu", "Denim", "Dusty", "Ekspreeso", 
                "Hitam", "Ivory", "Lemon", "Maroon", "Matcha", "Mauve", "Milo", "Mustard", "Navy", 
                "Olive", "Putih", "Salem", "Soft Blue", "Tanah", "Tarakota", "Tosca", "Wardah"
            ])

            operator = st.selectbox("Operator", ["Risman Sewing 1", "Rifa Sewing 2", "Wawan Sewing 3", "Febi Sewing 4", "Iman Sewing 5"])
            ukuran = st.selectbox("Ukuran", ["S", "M", "L"])
            workload = st.slider("Workload", 1, 100, 30)

            st.write("")
            predict_btn = st.button("🔵 Prediksi NG", use_container_width=True)
            
            rekomendasi_container = st.empty()

    # =====================================================
    # RESULT PANEL
    # =====================================================
    with right_col:
        with st.container(border=True):
            st.subheader("🤖 Hasil Analisis Prediksi")
            st.markdown("<p style='color: #64748B; font-size: 13.5px; margin-top: -8px; margin-bottom: 20px;'>Hasil klasifikasi machine learning beserta tingkat risikonya</p>", unsafe_allow_html=True)

            if predict_btn:
                try:
                    input_data = pd.DataFrame({
                        "tipe_barang": [tipe_barang],
                        "warna_kain": [warna_kain],
                        "operator": [operator],
                        "ukuran": [ukuran],
                        "workload": [workload]
                    })

                    prediction = model.predict(input_data)[0]
                    prediction_label = decode_prediction(prediction)
                    probabilities = model.predict_proba(input_data)[0]
                    max_prob = float(max(probabilities))

                    predicted_class = model.predict(input_data)[0]
                    kelas = [
                        "GOOD", "NG_JAHIT_LONCAT", "NG_NODA", 
                        "NG_PUCKER", "NG_ROBEK", "NG_TEPI_TIDAK_RAPI"
                    ]

                    max_prob = round(max(probabilities) * 100, 2)

                    risk = "RENDAH"
                    risk_color_hex = "#10B981"

                    if max_prob >= 60:
                        risk = "TINGGI"
                        risk_color_hex = "#EF4444"
                    elif max_prob >= 40:
                        risk = "SEDANG"
                        risk_color_hex = "#F59E0B"

                    is_good = (prediction_label == "GOOD")
                    card_accent_color = "#10B981" if is_good else "#EF4444"
                    pred_text_color = "#10B981" if is_good else "#EF4444"

                    waktu_sekarang = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame({
                        "Waktu": [waktu_sekarang],
                        "Tipe Barang": [tipe_barang],
                        "Operator": [operator],
                        "Prediksi": [prediction_label]
                    })
                    
                    # =========== DI SINI PERUBAHAN BATAS MAKSIMUM MENJADI 100 ===========
                    st.session_state.history = pd.concat([new_row, st.session_state.history], ignore_index=True).head(100)

                    st.markdown(f"""
                    <div class="prediction-box" style="border-left: 6px solid {card_accent_color} !important;">
                        <div style="font-size: 14px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;">Kategori Hasil</div>
                        <h1 style="color: {pred_text_color}; font-size: 36px; font-weight: 800; margin: 10px 0; font-family: sans-serif;">
                            {prediction_label}
                        </h1>
                        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 16px 0;">
                        <div style="display: flex; justify-content: space-around; align-items: center;">
                            <div style="flex: 1; text-align: center; border-right: 1px solid #E2E8F0;">
                                <div style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Probabilitas</div>
                                <div style="font-size: 24px; font-weight: 700; color: #0F172A; margin-top: 4px;">{max_prob}%</div>
                            </div>
                            <div style="flex: 1; text-align: center;">
                                <div style="font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Risk Level</div>
                                <div style="font-size: 24px; font-weight: 700; color: {risk_color_hex}; margin-top: 4px;">{risk}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write("")

                    st.markdown("<h4 style='color:#0F172A; font-weight:700; font-size:15px; margin-bottom:12px;'>📊 Probabilitas Setiap Kelas</h4>", unsafe_allow_html=True)

                    df_prob = pd.DataFrame({
                        "Kelas": kelas,
                        "Probabilitas": probabilities
                    })
                    
                    df_prob = df_prob.sort_values(by="Probabilitas", ascending=True)
                    text_labels = [f"{p:.2%}" if p > 0 else "" for p in df_prob["Probabilitas"]]

                    fig = go.Figure(go.Bar(
                        x=df_prob["Probabilitas"],
                        y=df_prob["Kelas"],
                        orientation="h",
                        text=text_labels,
                        textposition="auto",
                        marker=dict(color=df_prob["Probabilitas"], colorscale="Blues")
                    ))

                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#0F172A", height=260, margin=dict(l=20, r=20, t=10, b=10),
                        coloraxis_showscale=False,
                        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickformat=".0%"),
                        yaxis=dict(showgrid=False)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error dalam memproses prediksi: {e}")

            else:
                st.info("Silakan tentukan input data di kolom kiri lalu klik tombol Prediksi NG untuk melihat hasil analisis.")

    # =====================================================
    # MENGISI WADAH REKOMENDASI (Setelah Prediksi Selesai)
    # =====================================================
    if not st.session_state.history.empty:
        latest_pred = st.session_state.history.iloc[0]["Prediksi"]
        if latest_pred != "GOOD":
            rekomendasi = ""
            if latest_pred == "NG_PUCKER":
                rekomendasi = "Periksa tegangan benang pada mesin jahit. Pastikan jarum yang digunakan sesuai ketebalan kain, dan kurangi kecepatan jahit."
            elif latest_pred == "NG_JAHIT_LONCAT":
                rekomendasi = "Ganti jarum jahit karena kemungkinan tumpul atau bengkok. Pastikan pemasangan jalur benang (threading) sudah benar."
            elif latest_pred == "NG_NODA":
                rekomendasi = "Bersihkan area mesin jahit dari sisa oli. Pastikan tangan operator bersih dan area kerja bebas dari debu atau kotoran."
            elif latest_pred == "NG_ROBEK":
                rekomendasi = "Cek bagian gigi mesin jahit (feed dog) agar tidak terlalu tajam. Kurangi tarikan berlebih pada kain saat proses menjahit."
            elif latest_pred == "NG_TEPI_TIDAK_RAPI":
                rekomendasi = "Gunakan sepatu mesin jahit corong (hemmer foot) yang sesuai. Lakukan penyetelan pada pisau potong jika menggunakan mesin obras."
            
            if rekomendasi:
                rekomendasi_container.markdown(f"""
                <div style="margin-top: 15px; background: linear-gradient(145deg, #F8FAFC, #EFF6FF); border: 1px solid #BFDBFE; border-radius: 12px; padding: 18px; box-shadow: 0 4px 10px rgba(30, 58, 138, 0.03);">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 20px; margin-right: 10px;">💡</span>
                        <span style="color: #1E3A8A; font-weight: 800; font-size: 15px; font-family: 'Outfit', sans-serif; letter-spacing: 0.01em;">Rekomendasi Penanganan</span>
                    </div>
                    <div style="color: #334155; font-size: 13px; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 500;">
                        <span style="color: #EF4444; font-weight: 700;">{latest_pred}:</span> {rekomendasi}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # =====================================================
    # ANALYTICS SECTION (GRAFIK DINAMIS SESUAI HISTORY)
    # =====================================================
    st.write("")
    st.markdown("### 📈 Ringkasan & Analisis Tren Kualitas")
    st.write("")
    
    df_history = st.session_state.history.copy()
    df_ng = df_history[df_history["Prediksi"] != "GOOD"].copy()

    a1, a2, a3 = st.columns(3)

    with a1:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; font-weight:700; font-size:16px; margin-bottom:15px;'>Distribusi Jenis NG</h4>", unsafe_allow_html=True)

            if not df_ng.empty:
                pie_df = df_ng["Prediksi"].value_counts().reset_index()
                pie_df.columns = ["Jenis", "Jumlah"]
                fig_pie = px.pie(
                    pie_df, names="Jenis", values="Jumlah", hole=0.5,
                    color="Jenis",
                    color_discrete_sequence=["#EF4444", "#F59E0B", "#3B82F6", "#10B981", "#8B5CF6"]
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10), height=260, showlegend=False
                )
            else:
                fig_pie = go.Figure()
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260,
                    xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False),
                    annotations=[dict(text="Belum ada data NG", x=0.5, y=0.5, showarrow=False, font=dict(color="#94A3B8", size=14))]
                )
            st.plotly_chart(fig_pie, use_container_width=True)

    with a2:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; font-weight:700; font-size:16px; margin-bottom:15px;'>Trend NG Harian</h4>", unsafe_allow_html=True)

            if not df_ng.empty:
                df_ng["Tanggal"] = df_ng["Waktu"].apply(lambda x: x.split(" ")[0])
                trend_df = df_ng.groupby("Tanggal").size().reset_index(name="NG")
                trend_df["Tanggal_dt"] = pd.to_datetime(trend_df["Tanggal"], format="%d/%m/%Y")
                trend_df = trend_df.sort_values("Tanggal_dt")
                
                max_trend = trend_df["NG"].max()
                fig_line = px.line(trend_df, x="Tanggal", y="NG", markers=True, text="NG")
                fig_line.update_traces(
                    textposition="top center", 
                    line_color="#4F46E5", 
                    marker=dict(size=8, color="#3730A3")
                )
                fig_line.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=20, t=30, b=20), height=260,
                    xaxis=dict(showgrid=False, type='category', title=""), 
                    yaxis=dict(showgrid=True, gridcolor="#E2E8F0", dtick=1, title="", range=[0, max_trend + 1]) 
                )
            else:
                fig_line = go.Figure()
                fig_line.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260,
                    xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False),
                    annotations=[dict(text="Belum ada data NG", x=0.5, y=0.5, showarrow=False, font=dict(color="#94A3B8", size=14))]
                )
            st.plotly_chart(fig_line, use_container_width=True)

    with a3:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; font-weight:700; font-size:16px; margin-bottom:15px;'>Operator NG Tertinggi</h4>", unsafe_allow_html=True)

            if not df_ng.empty:
                df_ng["Operator_Singkat"] = df_ng["Operator"].apply(lambda x: x.split(" ")[0])
                op_df = df_ng["Operator_Singkat"].value_counts().reset_index()
                op_df.columns = ["Operator", "Jumlah"]
                op_df = op_df.head(5).sort_values("Jumlah", ascending=False)
                
                max_val = op_df["Jumlah"].max()
                
                fig_bar = px.bar(
                    op_df, x="Operator", y="Jumlah", orientation='v',
                    text="Jumlah"
                )
                
                fig_bar.update_traces(
                    marker_color="#3B82F6", 
                    textposition="outside",
                    textfont=dict(size=13, color="#0F172A", family="Outfit")
                )
                
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=20, t=30, b=20), height=260,
                    xaxis=dict(showgrid=False, title=""), 
                    yaxis=dict(showgrid=True, gridcolor="#E2E8F0", dtick=1, title="", range=[0, max_val + (max_val * 0.3) + 1]) 
                )
            else:
                fig_bar = go.Figure()
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260,
                    xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False),
                    annotations=[dict(text="Belum ada data NG", x=0.5, y=0.5, showarrow=False, font=dict(color="#94A3B8", size=14))]
                )
            st.plotly_chart(fig_bar, use_container_width=True)

    # =====================================================
    # HISTORY SECTION
    # =====================================================
    st.write("")
    with st.container(border=True):
        st.markdown("<h4 style='color:#0F172A; font-weight:700; font-size:17px; margin-bottom:15px;'>📋 Riwayat Prediksi</h4>", unsafe_allow_html=True)
        
        display_df = st.session_state.history.copy()
        display_df.insert(0, "No", range(1, len(display_df) + 1))

        col_table, col_actions = st.columns([3, 1], gap="medium")
        
        with col_table:
            st.dataframe(
                display_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "No": st.column_config.NumberColumn("No", width="small", format="%d"),
                    "Waktu": st.column_config.TextColumn("Waktu", width="medium"),
                    "Tipe Barang": st.column_config.TextColumn("Tipe Barang", width="large"),
                    "Operator": st.column_config.TextColumn("Operator", width="medium"),
                    "Prediksi": st.column_config.TextColumn("Prediksi", width="medium")
                }
            )
        
        with col_actions:
            st.markdown("<h5 style='font-size: 14px; margin-bottom: 8px;'>⚙️ Aksi Riwayat</h5>", unsafe_allow_html=True)
            
            data_bytes, file_ext, mime_type = get_download_data(display_df)
            st.download_button(
                label="📥 Export ke Excel" if file_ext == "xlsx" else "📥 Export ke CSV",
                data=data_bytes,
                file_name=f"riwayat_prediksi_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}",
                mime=mime_type,
                use_container_width=True
            )
            
            st.write("")
            
            if not display_df.empty:
                delete_options = [f"{row['No']}. {row['Tipe Barang']} ({row['Waktu'].split()[-1]}) - {row['Prediksi']}" for i, row in display_df.iterrows()]
                selected_del = st.selectbox("Pilih baris untuk dihapus:", delete_options, key="delete_select_box")
                
                if st.button("🗑️ Hapus Baris", use_container_width=True):
                    idx_del = delete_options.index(selected_del)
                    st.session_state.history = st.session_state.history.drop(st.session_state.history.index[idx_del]).reset_index(drop=True)
                    st.rerun()
            else:
                st.caption("Tidak ada riwayat untuk dihapus.")

# =====================================================
# ABOUT PAGE
# =====================================================
elif menu == "ℹ️ Tentang Sistem":
    st.markdown('<div class="title-dashboard">Tentang Sistem Smart Quality Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-dashboard">Ameena Baby & Kids Store - Monitoring Kualitas Produksi</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("💡 Latar Belakang & Deskripsi Sistem")
        st.markdown("""
        Dashboard ini dirancang untuk mendeteksi potensi **Not Good (NG)** pada proses produksi hijab anak di Ameena Baby & Kids Store secara dini.
        
        Dengan memanfaatkan algoritma pembelajaran mesin seperti **Random Forest** dan **Support Vector Machine (SVM)**, sistem ini menganalisis variabel produksi seperti jenis barang, warna kain, operator sewing, ukuran, serta beban kerja (*workload*) untuk mengklasifikasikan apakah suatu produk masuk kategori kualitas **GOOD** atau memiliki cacat (NG) tertentu:
        - **NG_JAHIT_LONCAT**
        - **NG_NODA**
        - **NG_PUCKER** (kerutan kain)
        - **NG_ROBEK**
        - **NG_TEPI_TIDAK_RAPI**
        
        Sistem ini memfasilitasi pengambilan keputusan proaktif guna menekan tingkat cacat produk dan menjaga konsistensi kualitas produk yang dikirimkan ke pelanggan.
        """)

st.markdown("---")
st.caption("© 2026 Smart Quality Control Dashboard - Ameena Baby & Kids Store. All rights reserved.")
