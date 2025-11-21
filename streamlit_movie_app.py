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

# Modern karanlık tema CSS tasarımı
st.markdown("""
<style>
    /* Ana tema renkleri */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
    }
    
    /* Genel arka plan ve yazı tipi */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        background-attachment: fixed;
    }
    
    .main {
        background: transparent;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(15, 23, 42, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Başlık stilleri */
    h1 {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    
    /* Tüm yazılar için varsayılan renk */
    p, span, label, div {
        color: #e2e8f0 !important;
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
        background: #1e293b;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f172a;
        border-radius: 12px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        background: #1e293b;
        color: #94a3b8 !important;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #334155;
        border-color: #667eea;
        color: #e2e8f0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    /* Form stilleri */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
    min-height: 48px !important;    
    line-height: 1.4 !important; 
    },
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #334155 !important;
        background: #1e293b !important;
        color: #e2e8f0 !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox input[type="text"] {
    line-height: 1.4 !important; /* Satır yüksekliğini garanti et */
    height: auto !important;     /* Yüksekliğin içeriğe göre otomatik ayarlanmasını sağla */
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        background: #0f172a !important;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="popover"] {
        background: #1e293b !important;
    }
    
    [data-baseweb="select"] > div {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        display: flex !important;
        align-items: center !important; 
        height: 100% !important;
    }
    
    /* Placeholder renkleri */
    input::placeholder, textarea::placeholder {
        color: #64748b !important;
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
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 16px;
        color: #e2e8f0 !important;
    }
    
    .stAlert > div {
        color: #e2e8f0 !important;
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
        background: #1e293b;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    .stRadio label {
        color: #e2e8f0 !important;
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
        color: #f1f5f9 !important;
        font-weight: 700;
    }
    
    /* Özel kart tasarımı */
    .custom-card {
        background: #1e293b;
        border-radius: 15px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
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
    data = ws.get_all_values()
    
    if not data:
        return pd.DataFrame()
        
    headers = data[0]
    records = data[1:]
    df = pd.DataFrame(records, columns=headers)
    return df

# WRITE (append row)
def append_row(sheet_name, row_list):
    sheet = connect_google_sheets()
    ws = sheet.worksheet(sheet_name)
    ws.append_row(row_list)

@st.cache_data(ttl=60) 
def load_movies():
    df = load_sheet("movies")
    if df.empty or 'title' not in df.columns:
        return pd.DataFrame(columns=["type", "title"])
    return df

@st.cache_data(ttl=60)
def load_ratings():
    df = load_sheet("ratings")
    if df.empty or 'title' not in df.columns:
        return pd.DataFrame(columns=["type", "title", "rating", "comment", "user", "created_at"])
    return df

@st.cache_data(ttl=60)
def load_watchlist():
    df = load_sheet("watchlist")
    
    # Beklenen sütunlar
    expected_cols = ["type", "title", "user", "created_at"]
    
    # Eğer gelen veri boşsa, boş template döndür
    if df.empty:
        return pd.DataFrame(columns=expected_cols)
    
    # Sütun isimlerini küçük harfe çevir ve boşlukları temizle (Hata önleyici)
    df.columns = df.columns.str.lower().str.strip()
    
    # Eksik sütun kontrolü: Eğer 'title' yoksa veri bozuktur, boş döndür
    if not set(expected_cols).issubset(df.columns):
        # Sütunlar eksikse bile kodun patlamaması için boş sütunları ekleyelim
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
                
    return df

def save_movie(entry):
    row_list = [entry["type"], entry["title"]]
    append_row("movies", row_list)
    load_movies.clear()

def save_rating(entry):
    row_list = [
        entry["type"], entry["title"], entry["rating"],
        entry["comment"], entry["user"], entry["created_at"]
    ]
    append_row("ratings", row_list)
    load_ratings.clear()

def delete_from_watchlist(title, user):
    sheet = connect_google_sheets()
    ws = sheet.worksheet("watchlist")
    data = ws.get_all_values()

    # Başlık hariç satırları kontrol et
    # Google Sheets API'de satır numaraları 1'den başlar, başlık 1. satır ise veri 2'den başlar.
    # enumerate içinde index 0'dan başlar, bu yüzden start=2 diyerek Sheet satırına denk getiriyoruz.
    rows_to_delete = []
    
    for idx, row in enumerate(data):
        if idx == 0: continue # Başlığı atla
        # row listesi indexleri: 0=type, 1=title, 2=user
        if len(row) > 2 and row[1] == title and row[2] == user:
            # Silinecek satırın gerçek sheet numarası (idx + 1)
            rows_to_delete.append(idx + 1)
            
    # Sondan başa doğru sil ki indexler kaymasın
    for row_num in reversed(rows_to_delete):
        ws.delete_rows(row_num)

    load_watchlist.clear()

def save_watchlist(entry):
    append_row("watchlist", [
        entry["type"],
        entry["title"],
        entry["user"],
        entry["created_at"]
    ])
    load_watchlist.clear()



# --- HEADER & METRİKLER ---
st.title("🎬")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem; margin-top: -10px;'></p>", unsafe_allow_html=True)

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
tab_vote, tab_top10, tab_profile, tab_watchlist, tab_recommend, tab_data = st.tabs([
    "✍️ Oy Ver & Ekle",
    "🏆 Top 10 Listesi",
    "👤 Kullanıcı Profili",
    "📌 Watchlist",
    "🎲 Öneri Makinesi",
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
#   TAB 4: WATCHLIST
# ==============================================================================
with tab_watchlist:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("📌 Watchlist")

    watchlist_df = load_watchlist()

    # Veri kontrolü: Boş mu veya gerekli sütunlar eksik mi?
    if watchlist_df.empty:
        st.info("📭 Watchlist şu an boş.")
    elif "user" not in watchlist_df.columns:
        st.error("⚠️ Watchlist verisi okunurken bir hata oluştu (Sütun başlıkları eksik). Lütfen Google Sheet'i kontrol edin.")
    else:
        users = watchlist_df["user"].unique()
        selected_user = st.selectbox("👤 Kullanıcı", users, key="wl_user_select")

        user_wl = watchlist_df[watchlist_df["user"] == selected_user]

        if user_wl.empty:
            st.info("📭 Bu kullanıcının watchlist’i boş.")
        else:
            # Güvenli sütun seçimi
            cols_to_show = [col for col in ["type", "title", "created_at"] if col in user_wl.columns]
            
            st.dataframe(
                user_wl[cols_to_show],
                use_container_width=True,
                hide_index=True
            )
            
            # Silme opsiyonu ekleyelim (Opsiyonel Geliştirme)
            to_delete = st.selectbox("Listeden silmek istediğin var mı?", ["Seçiniz..."] + user_wl["title"].tolist())
            if to_delete != "Seçiniz...":
                if st.button(f"🗑️ {to_delete} sil"):
                    delete_from_watchlist(to_delete, selected_user)
                    st.success("Silindi!")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
#   TAB: RASTGELE ÖNERİ MAKİNESİ (SADECE WATCHLIST'TEN SEÇER)
# ==============================================================================
with tab_recommend:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("🎲 Rastgele Film & Dizi Önerisi")

    watchlist_df = load_watchlist()

    if watchlist_df.empty:
        st.info("📭 Watchlist boş.")
    else:
        users = watchlist_df["user"].unique()
        selected_user = st.selectbox("👤 Kullanıcı", users)

        user_wl = watchlist_df[watchlist_df["user"] == selected_user]

        movies = user_wl[user_wl["type"] == "Film"]["title"].tolist()
        shows  = user_wl[user_wl["type"] == "Dizi"]["title"].tolist()

        col1, col2 = st.columns(2)

        with col1:
            st.write("🎬 Filmler")
            chosen_movies = st.multiselect("Seçim yapılacak filmler", movies, default=movies)
            if st.button("🎯 Rastgele Film"):
                if chosen_movies:
                    st.success(f"🎬 {pd.Series(chosen_movies).sample(1).iloc[0]}")
                else:
                    st.warning("Film seçilmedi.")

        with col2:
            st.write("📺 Diziler")
            chosen_shows = st.multiselect("Seçim yapılacak diziler", shows, default=shows)
            if st.button("🎯 Rastgele Dizi"):
                if chosen_shows:
                    st.success(f"📺 {pd.Series(chosen_shows).sample(1).iloc[0]}")
                else:
                    st.warning("Dizi seçilmedi.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
#   TAB 5: TÜM VERİLER (RAW DATA)
# ==============================================================================
with tab_data:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.subheader("💾 Veritabanı")
    
    with st.expander("🎬 Filmler Listesi", expanded=False):
        st.dataframe(movies_df, use_container_width=True, hide_index=True)

    with st.expander("⭐ Tüm Oylar", expanded=True):
        st.dataframe(ratings_df, use_container_width=True, hide_index=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
