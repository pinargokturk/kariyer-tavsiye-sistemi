import streamlit as st
import pypdf
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
import os

from nlp_preprocessing import clean_text
from extract_skills import extract_skills_from_text, SKILL_DICTIONARY

# Sayfa Yapılandırması
st.set_page_config(
    page_title="AI Kariyer & İş Tavsiye Portalı",
    page_icon="💼",
    layout="wide"
)

# 1. Modelleri Önbelleğe Alarak Yükleme
@st.cache_resource
def load_ml_components():
    with open("tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open("jobs_metadata.pkl", "rb") as f:
        jobs_df = pickle.load(f)
    return vectorizer, tfidf_matrix, jobs_df

vectorizer, tfidf_matrix, jobs_df = load_ml_components()

# 2. Veri Tabanı Yardımcı Fonksiyonu
def get_job_skills_from_db(job_id):
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.skill_name 
        FROM skills s 
        JOIN job_skills js ON s.skill_id = js.skill_id 
        WHERE js.job_id = %s;
    """, (int(job_id),))
    skills = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return set(skills)

# 3. PDF'ten Metin Çıkarma Fonksiyonu
def extract_text_from_pdf(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + " "
    return extracted_text

# --- ARAYÜZ (UI) TASARIMI ---
st.title("💼 AI Destekli Kariyer & İş Tavsiye Portalı")

# Sekme Mimarisi
tab1, tab2 = st.tabs(["🎯 İş Eşleştirme & Tavsiye", "📊 Piyasa Analitiği & İçgörüler"])

with tab1:
    st.markdown("Özgeçmişinizi (PDF) yükleyin veya yeteneklerinizi girin; yapay zeka en uygun işleri ve eksik becerilerinizi çıkarsın.")

    # Sol Panel (Sidebar)
    st.sidebar.header("⚙️ Aday Profili Girdisi")
    input_method = st.sidebar.radio("Girdi Yöntemi Seçin:", ("PDF CV Yükle", "Manuel Metin / Yetenek Girişi"))
    top_n = st.sidebar.slider("Önerilecek İlan Sayısı:", min_value=3, max_value=10, value=5)

    user_raw_text = ""

    if input_method == "PDF CV Yükle":
        uploaded_file = st.sidebar.file_uploader("Özgeçmişinizi (PDF) yükleyin", type=["pdf"])
        if uploaded_file is not None:
            user_raw_text = extract_text_from_pdf(uploaded_file)
            st.sidebar.success("✅ PDF başarıyla okundu!")
    else:
        user_raw_text = st.sidebar.text_area(
            "Teknik beceri veya deneyim özeti:",
            value="Python, SQL, Machine Learning, PostgreSQL, Pandas, Docker",
            height=150
        )

    analyze_button = st.sidebar.button("🔍 İş Fırsatlarını Analiz Et", type="primary")

    if analyze_button:
        if not user_raw_text.strip():
            st.warning("⚠️ Lütfen bir PDF yükleyin veya metin girin.")
        else:
            detected_skills = set(extract_skills_from_text(user_raw_text, SKILL_DICTIONARY))
            
            st.subheader("👤 Profilinizde Tespit Edilen Yetenekler")
            if detected_skills:
                st.write(" ".join([f"`{skill}`" for skill in sorted(detected_skills)]))
            else:
                st.info("Sözlükte eşleşen spesifik bir teknik terim bulunamadı; genel anlamsal eşleme yapılıyor.")

            # Tavsiye Hesaplama
            cleaned_input = clean_text(user_raw_text)
            user_vector = vectorizer.transform([cleaned_input])
            similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
            top_indices = similarities.argsort()[::-1][:top_n]

            st.markdown("---")
            st.subheader("🎯 Size En Uygun Pozisyonlar ve Kariyer Açığı Analizi")

            for rank, idx in enumerate(top_indices, 1):
                job_id = jobs_df.iloc[idx]['job_id']
                title = jobs_df.iloc[idx]['title']
                company = jobs_df.iloc[idx]['company'] if 'company' in jobs_df.columns else "Şirket Bilgisi Belirtilmemiş"
                score = similarities[idx] * 100

                job_skills = get_job_skills_from_db(job_id)
                matched = detected_skills.intersection(job_skills)
                missing = job_skills.difference(detected_skills)
                coverage = (len(matched) / len(job_skills) * 100) if job_skills else 100.0

                with st.expander(f"#{rank} - {title} | {company} (Uyum Skoru: %{score:.1f})", expanded=(rank == 1)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Metin Benzerlik Skoru", f"%{score:.1f}")
                        st.metric("Yetenek Kapsama Oranı", f"%{coverage:.1f}")
                    with col2:
                        st.markdown("**İlanda Aranan Beceriler:**")
                        st.write(", ".join(sorted(job_skills)) if job_skills else "Genel profil")
                    
                    st.markdown("---")
                    c_match, c_miss = st.columns(2)
                    with c_match:
                        st.success(f"**Eşleşen Yetenekleriniz ({len(matched)}):**\n" + (", ".join(sorted(matched)) if matched else "Doğrudan eşleşme yok"))
                    with c_miss:
                        if missing:
                            st.error(f"**Geliştirilmesi Gereken Beceriler ({len(missing)}):**\n" + ", ".join(sorted(missing)))
                        else:
                            st.info("Bu ilanın tüm teknik gereksinimlerini karşılıyorsunuz!")

with tab2:
    st.subheader("📈 Veri Bilimi Sektörel Beceri & Terim Trendleri")
    st.markdown("Veri tabanında yer alan 3.699 iş ilanından derlenen keşifsel veri analizleri:")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**En Çok Talep Edilen İlk 15 Teknoloji**")
        skills_img_path = "staj_kanitlari/eda_top_15_skills.png"
        if os.path.exists(skills_img_path):
            st.image(skills_img_path, use_container_width=True)
        else:
            st.warning("Grafik bulunamadı. Lütfen önce `eda_visualization.py` dosyasını çalıştırın.")

    with col_chart2:
        st.markdown("**İş Tanımları Sektörel Kelime Bulutu**")
        wc_img_path = "staj_kanitlari/eda_wordcloud.png"
        if os.path.exists(wc_img_path):
            st.image(wc_img_path, use_container_width=True)
        else:
            st.warning("Kelime bulutu bulunamadı.")