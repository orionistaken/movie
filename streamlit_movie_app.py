import streamlit as st
import pandas as pd
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Film & Dizi Kulübü",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Özel CSS ile biraz makyaj yapalım (Tabloları ve başlıkları güzelleştirir)
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #dcdcdc;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
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
    data = sheet.worksheet(sheet_name).get_all_records()
    return pd.DataFrame(data)

# WRITE (append row)
def append_row(sheet_name, row_list):
    sheet = connect_google_sheets()
    ws = sheet.worksheet(sheet_name)
    ws.append_row(row_list)

# -------------------------------------------------------------------
#   YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------

@st.cache_data(ttl=600)
def load_movies():
    # gspread fonksiyonunu çağırır
    return load_sheet("movies")

@st.cache_data(ttl=600)
def load_ratings():
    # gspread fonksiyonunu çağırır
    return load_sheet("ratings")

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
st.title("🍿 Film & Dizi Kulübü")
st.markdown("Arkadaşlarınla izlediklerini puanla, yorumla ve keşfet!")

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
        avg_all = ratings_df["rating"].mean()
        st.metric("📊 Genel Ortalama", f"{avg_all:.2f}")
    else:
        st.metric("📊 Genel Ortalama", "-")

st.divider()

# --- TAB YAPISI (MENÜ YERİNE) ---
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
    # İki sütuna bölelim: Sol taraf OY VERME, Sağ taraf YENİ EKLEME
    col_left, col_right = st.columns([2, 1], gap="large")

    # --- SOL: OY VERME ---
    with col_left:
        st.subheader("⭐ Puanını Yapıştır")

        if movies_df.empty:
            st.info("Listede henüz film yok. Sağ taraftan ekleyebilirsin 👉")
        else:
            # Form kullanımı: Sayfa her harf girişinde yenilenmez, butona basınca işlem yapar.
            with st.form("rating_form"):
                selected_movie = st.selectbox("Hangi yapım?", movies_df["title"].unique())

                c1, c2 = st.columns(2)
                with c1:
                    rating = st.number_input("Puanın (0-10)", 0.0, 10.0, step=0.1, format="%.1f")
                with c2:
                    user = st.text_input("Kullanıcı Adın (Zorunlu)")

                comment = st.text_area("Yorumun (Varsa)", height=80, placeholder="Bence harikaydı çünkü...")

                submitted = st.form_submit_button("Oyu Kaydet", use_container_width=True)

                if submitted:
                    if not user.strip():
                        st.error("⚠️ Kim olduğunu bilmemiz lazım! Lütfen ismini gir.")
                    else:
                        # Türü bul
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

    # --- SAĞ: YENİ FİLM EKLEME ---
    with col_right:
        st.info("Aradığın film listede yok mu?")
        with st.expander("➕ Yeni Ekle", expanded=True):
            with st.form("add_movie_form"):
                new_type = st.radio("Tür", ["Film", "Dizi"], horizontal=True)
                new_title = st.text_input("Adı nedir?")
                add_submitted = st.form_submit_button("Listeye Ekle")

                if add_submitted:
                    if new_title.strip():
                        # Aynı isimde var mı kontrol et
                        if new_title in movies_df["title"].values:
                            st.warning("Bu zaten listede var!")
                        else:
                            save_movie({"type": new_type, "title": new_title})
                            st.success(f"✔ {new_title} eklendi! Şimdi yanda oylayabilirsin.")
                            st.rerun()  # Listeyi yenilemek için sayfayı tazeleyin
                    else:
                        st.error("Bir isim girmelisin.")

# ==============================================================================
#   TAB 2: TOP 10 LİSTESİ
# ==============================================================================
with tab_top10:
    st.subheader("🏆 Zirvedekiler")

    if ratings_df.empty:
        st.warning("Henüz yeterli veri yok.")
    else:
        # Gruplama ve ortalama alma
        stats = ratings_df.groupby("title").agg(
            Ortalama_Puan=('rating', 'mean'),
            Oy_Sayisi=('rating', 'count')
        ).reset_index()

        # Sıralama: Hem puana hem de oy sayısına göre (eşitlikte oy sayısı çok olan üstte)
        top_list = stats.sort_values(by=["Ortalama_Puan", "Oy_Sayisi"], ascending=False).head(10)

        # Görselleştirme
        # İndeksi 1'den başlat
        top_list.index = range(1, len(top_list) + 1)

        st.dataframe(
            top_list.style.background_gradient(subset=["Ortalama_Puan"], cmap="Greens"),
            use_container_width=True,
            column_config={
                "title": "Yapım Adı",
                "Ortalama_Puan": st.column_config.NumberColumn("Puan", format="%.2f ⭐"),
                "Oy_Sayisi": st.column_config.NumberColumn("Kişi Sayısı", format="%d 👤")
            }
        )

# ==============================================================================
#   TAB 3: KULLANICI PROFİLİ
# ==============================================================================
with tab_profile:
    if ratings_df.empty:
        st.warning("Henüz kimse oy vermemiş.")
    else:
        col_sel, col_detail = st.columns([1, 3])

        with col_sel:
            users = ratings_df["user"].unique()
            selected_user = st.selectbox("Kullanıcı Seç", users)

            # Kullanıcı özeti
            user_data = ratings_df[ratings_df["user"] == selected_user]
            u_avg = user_data["rating"].mean()
            u_count = len(user_data)

            st.markdown(f"""
            <div style="background-color:#e8f4f8; padding:15px; border-radius:10px; margin-top:20px;">
                <h3 style="margin:0; color:#0e1117;">{selected_user}</h3>
                <p>Ortalama: <b>{u_avg:.2f}</b></p>
                <p>Toplam Oy: <b>{u_count}</b></p>
            </div>
            """, unsafe_allow_html=True)

        with col_detail:
            st.subheader(f"📋 {selected_user} Geçmişi")
            # Tabloyu güzel gösterelim
            display_df = user_data[["title", "rating", "comment", "created_at"]].sort_values("created_at",
                                                                                             ascending=False)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "title": "Film/Dizi",
                    "rating": st.column_config.NumberColumn("Puan", format="%.1f"),
                    "comment": "Yorum",
                    "created_at": "Tarih"
                }
            )

# ==============================================================================
#   TAB 4: TÜM VERİLER (RAW DATA)
# ==============================================================================
with tab_data:
    st.subheader("💾 Veritabanı")
    with st.expander("Filmler Listesi", expanded=False):
        st.dataframe(movies_df, use_container_width=True)

    with st.expander("Tüm Oylar", expanded=True):
        st.dataframe(ratings_df, use_container_width=True)
