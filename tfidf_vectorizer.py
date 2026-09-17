import psycopg2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from nlp_preprocessing import clean_text

def build_tfidf_model():
    print("📥 1. Adım: Veri tabanından ilanlar çekiliyor...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    df = pd.read_sql("SELECT job_id, title, description FROM job_postings;", conn)
    conn.close()
    print(f"   -> Toplam {len(df)} ilan çekildi.")

    print("\n⚙️  2. Adım: Metinler NLP pipeline'ı ile temizleniyor...")
    df['cleaned_description'] = df['description'].apply(clean_text)

    print("\n📐 3. Adım: TF-IDF matrisi hesaplanıyor...")
    # max_features=5000: En ayırt edici 5.000 kelimeyi alıyoruz
    # ngram_range=(1,2): Hem tekil kelimeleri ('python') hem ikili kalıpları ('data science', 'machine learning') yakalar
    # min_df=2: En az 2 ilanda geçmeyen çok nadir/hatalı kelimeleri eler
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2
    )
    
    tfidf_matrix = vectorizer.fit_transform(df['cleaned_description'])
    
    print("✅ TF-IDF Modeli Başarıyla Oluşturuldu!")
    print(f"📊 Vektör Matrisi Boyutu (İlan Sayısı, Öznitelik Sayısı): {tfidf_matrix.shape}")
    print(f"🧠 Sözlükteki İlk 15 Terim / İkili Kalıp: {vectorizer.get_feature_names_out()[:15]}")

    # Modeli ve matrisi ileride tavsiye motorunda tekrar hesaplamadan kullanmak için kaydediyoruz
    print("\n💾 4. Adım: Model ve matris diske kaydediliyor...")
    with open("tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)
    with open("jobs_metadata.pkl", "wb") as f:
        pickle.dump(df[['job_id', 'title']], f)
        
    print("🔒 Dosyalar başarıyla diske yazıldı (tfidf_vectorizer.pkl, tfidf_matrix.pkl, jobs_metadata.pkl).")

if __name__ == "__main__":
    build_tfidf_model()