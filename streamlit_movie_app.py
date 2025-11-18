import streamlit as st
import pandas as pd
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Filmler",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern ve şık CSS tasarımı
st.markdown("""
<style>
    /* Ana tema renkleri */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    /* Genel arka plan ve yazı tipi */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Başlık stilleri */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    
    /* Metrik kutucukları */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        border: none;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stMetric label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Tab stilleri */
    .stTabs {
        background: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        border-radius: 12px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        background: white;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        border-color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    /* Form stilleri */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buton stilleri */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Info kutusu */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 16px;
    }
    
    /* Expander stilleri */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 10px;
        padding: 16px;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #5558e3 0%, #6d409b 100%);
    }
    
    /* Dataframe stilleri */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Radio button stilleri */
    .stRadio > div {
        background: #f8fafc;
        padding: 12px;
        border-radius: 10px;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Alt başlıklar */
    h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }
    
    /* Özel kart tasarımı */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def connect_google_sheets():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(credentials)
    sheet_id = st.secrets["sheets"]["sheet_id"]
    sheet = client.open_by_key(sheet_id)
    return sheet

# READ
def load_sheet(sheet_name):
    sheet = connect_google_sheets()
    ws = sheet.worksheet(sheet_name)
    
    # Tüm veriyi A1'den itibaren liste formatında çek (başlık dahil)
    data = ws.get_all_values()
    
    if not data:
        # Sheet tamamen boşsa (başlık bile yoksa) boş DataFrame döndür
        return pd.DataFrame()
        
    # İlk satırı başlık olarak al
    headers = data[0]
    # Geri kalan satırları veri olarak al
    records = data[1:]
    
    # DataFrame'i başlıklar ve verilerle oluştur
    df = pd.DataFrame(records, columns=headers)
    
    return df

# WRITE (append row)
def append_row(sheet_name, row_list):
    sheet = connect_google_sheets()
    ws = sheet.worksheet(sheet_name)
    ws.append_row(row_list)

# -------------------------------------------------------------------
#   YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------

@st.cache_data(ttl=60) 
def load_movies():
    df = load_sheet("movies")
    # DataFrame boşsa veya sütun yoksa, beklenen sütunlarla boş DataFrame döndür
    if df.empty or 'title' not in df.columns:
        return pd.DataFrame(columns=["type", "title"])
    return df

@st.cache_data(ttl=60)
def load_ratings():
    df = load_sheet("ratings")
    if df.empty or 'title' not in df.columns:
        return pd.DataFrame(columns=["type", "title", "rating", "comment", "user", "created_at"])
    return df

def save_movie(entry):
    # Sözlük (dict) olarak gelen veriyi, gspread'in istediği liste (list) formatına dönüştürür.
    row_list = [entry["type"], entry["title"]]
    append_row("movies", row_list)
    # Veriyi yazdıktan sonra önbelleği temizleyin
    load_movies.clear()

def save_rating(entry):
    # Sözlük (dict) olarak gelen veriyi, gspread'in istediği liste (list) formatına dönüştürür.
    row_list = [
        entry["type"], entry["title"], entry["rating"],
        entry["comment"], entry["user"], entry["created_at"]
    ]
    append_row("ratings", row_list)
    # Veriyi yazdıktan sonra önbelleği temizleyin
    load_ratings.clear()


# --- HEADER & METRİKLER ---
st.title("🎬 Filmler")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-top: -10px;'>Arkadaşlarınla izlediklerini puanla, yorumla ve keşfet!</p>", unsafe_allow_html=True)

# Verileri çekelim
movies_df = load_movies()
ratings_df = load_ratings()

# Üstte istatistikleri gösteren şık kutucuklar
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎬 Toplam İçerik", len(movies_df))
with col2:
    st.metric("⭐ Toplam Oy", len(ratings_df))
with col3:
    if not ratings_df.empty:
        avg_all = pd.to_numeric(ratings_df["rating"], errors='coerce').mean()
        st.metric("📊 Genel Ortalama", f"{avg_all:.2f}")
    else:
        st.metric("📊 Genel Ortalama", "-")

st.divider()

# --- TAB YAPISI ---
tab_vote, tab_top10, tab_profile, tab_data = st.tabs([
    "✍️ Oy Ver & Ekle",
    "🏆 Top 10 Listesi",
    "👤 Kullanıcı Profili",
    "📂 Tüm Veriler"
])

# ==============================================================================
#   TAB 1: OY VERME ve EKLEME MERKEZİ
# ==============================================================================
with tab_vote:
    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("⭐ Puanını Yapıştır")

        if movies_df.empty:
            st.info("📽️ Listede henüz film yok. Sağ taraftan ekleyebilirsin 👉")
        else:
            with st.form("rating_form"):
                selected_movie = st.selectbox("Hangi yapım?", movies_df["title"].unique(), help="İzlediğin filmi seç")

                c1, c2 = st.columns(2)
                with c1:
                    rating = st.number_input("Puanın (0-10)", 0.0, 10.0, step=0.1, format="%.1f", help="0-10 arası puan ver")
                with c2:
                    user = st.text_input("Kullanıcı Adın", placeholder="Örn: Ahmet")

                comment = st.text_area("Yorumun", height=100, placeholder="Bence harikaydı çünkü...", help="İsteğe bağlı")

                submitted = st.form_submit_button("🎯 Oyu Kaydet", use_container_width=True)

                if submitted:
                    if not user.strip():
                        st.error("⚠️ Kim olduğunu bilmemiz lazım! Lütfen ismini gir.")
                    else:
                        m_type = movies_df[movies_df["title"] == selected_movie]["type"].iloc[0]
                        entry = {
                            "type": m_type,
                            "title": selected_movie,
                            "rating": rating,
                            "comment": comment,
                            "user": user,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        save_rating(entry)
                        st.success(f"✅ {selected_movie} için oyun kaydedildi!")
                        st.balloons()
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.info("🔍 Aradığın film listede yok mu?")
        with st.expander("➕ Yeni Ekle", expanded=True):
            with st.form("add_movie_form"):
                new_type = st.radio("Tür", ["Film", "Dizi"], horizontal=True)
                new_title = st.text_input("Adı nedir?", placeholder="Örn: Inception")
                add_submitted = st.form_submit_button("📌 Listeye Ekle", use_container_width=True)

                if add_submitted:
                    if new_title.strip():
                        if new_title in movies_df["title"].values:
                            st.warning("⚠️ Bu zaten listede var!")
                        else:
                            save_movie({"type": new_type, "title": new_title})
                            st.success(f"✅ {new_title} eklendi!")
                            st.rerun()
                    else:
                        st.error("❌ Bir isim girmelisin.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
#   TAB 2: TOP 10 LİSTESİ
# ==============================================================================
with tab_top10:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("🏆 Zirvedekiler")

    if ratings_df.empty:
        st.warning("⏳ Henüz yeterli veri yok.")
    else:
        ratings_numeric = ratings_df.copy()
        ratings_numeric["rating"] = pd.to_numeric(ratings_numeric["rating"], errors='coerce')
        
        stats = ratings_numeric.groupby("title").agg(
            Ortalama_Puan=('rating', 'mean'),
            Oy_Sayisi=('rating', 'count')
        ).reset_index()

        top_list = stats.sort_values(by=["Ortalama_Puan", "Oy_Sayisi"], ascending=False).head(10)
        top_list.index = range(1, len(top_list) + 1)

        st.dataframe(
            top_list.style.background_gradient(subset=["Ortalama_Puan"], cmap="RdYlGn"),
            use_container_width=True,
            column_config={
                "title": st.column_config.TextColumn("🎬 Yapım Adı", width="large"),
                "Ortalama_Puan": st.column_config.NumberColumn("⭐ Puan", format="%.2f"),
                "Oy_Sayisi": st.column_config.NumberColumn("👥 Kişi Sayısı", format="%d")
            }
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
#   TAB 3: KULLANICI PROFİLİ
# ==============================================================================
with tab_profile:
    if ratings_df.empty:
        st.warning("⏳ Henüz kimse oy vermemiş.")
    else:
        col_sel, col_detail = st.columns([1, 3])

        with col_sel:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            users = ratings_df["user"].unique()
            selected_user = st.selectbox("👤 Kullanıcı Seç", users)

            user_data = ratings_df[ratings_df["user"] == selected_user].copy()
            user_data["rating"] = pd.to_numeric(user_data["rating"], errors='coerce')
            u_avg = user_data["rating"].mean()
            u_count = len(user_data)

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 15px; margin-top: 20px; color: white;
                        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);">
                <h2 style="margin:0; color: white; font-size: 1.5rem;">🎭 {selected_user}</h2>
                <p style="font-size: 1.1rem; margin-top: 10px;">⭐ Ortalama: <b>{u_avg:.2f}</b></p>
                <p style="font-size: 1.1rem;">📊 Toplam Oy: <b>{u_count}</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_detail:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            st.subheader(f"📋 {selected_user} Geçmişi")
            display_df = user_data[["title", "rating", "comment", "created_at"]].sort_values(
                "created_at", ascending=False
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "title": st.column_config.TextColumn("🎬 Film/Dizi", width="medium"),
                    "rating": st.column_config.NumberColumn("⭐ Puan", format="%.1f"),
                    "comment": st.column_config.TextColumn("💬 Yorum", width="large"),
                    "created_at": st.column_config.TextColumn("📅 Tarih")
                }
            )
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
#   TAB 4: TÜM VERİLER (RAW DATA)
# ==============================================================================
with tab_data:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("💾 Veritabanı")
    
    with st.expander("🎬 Filmler Listesi", expanded=False):
        st.dataframe(movies_df, use_container_width=True, hide_index=True)

    with st.expander("⭐ Tüm Oylar", expanded=True):
        st.dataframe(ratings_df, use_container_width=True, hide_index=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
