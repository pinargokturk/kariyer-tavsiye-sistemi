import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nlp_preprocessing import clean_text

def load_artifacts():
    # Kaydettiğimiz modelleri yüklüyoruz
    with open("tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open("jobs_metadata.pkl", "rb") as f:
        jobs_df = pickle.load(f)
    return vectorizer, tfidf_matrix, jobs_df

def recommend_jobs(user_skills, top_n=5):
    vectorizer, tfidf_matrix, jobs_df = load_artifacts()
    
    # 1. Kullanıcı girdisini NLP pipeline'ından geçiriyoruz
    cleaned_input = clean_text(user_skills)
    
    # 2. Girdiyi TF-IDF vektörüne dönüştürüyoruz
    user_vector = vectorizer.transform([cleaned_input])
    
    # 3. Kosinüs Benzerliği hesaplama (1 x 3699 benzerlik skoru dizisi)
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    
    # 4. En yüksek skora sahip top_n ilanın indekslerini alıyoruz
    top_indices = similarities.argsort()[::-1][:top_n]
    
    print("=" * 65)
    print(f"🎯 GİRİLEN BECERİLER: {user_skills}")
    print(f"🧹 TEMİZLENMİŞ GİRDİ : {cleaned_input}")
    print("=" * 65)
    print(f"🏆 EN UYGUN İLK {top_n} İŞ İLANI TAVSİYESİ:\n")
    
    results = []
    for rank, idx in enumerate(top_indices, 1):
        job_id = jobs_df.iloc[idx]['job_id']
        title = jobs_df.iloc[idx]['title']
        score = similarities[idx]
        
        print(f"{rank}. [Skor: %{score * 100:.2f}] (İlan ID: {job_id}) {title}")
        results.append((job_id, title, score))
        
    return results

if __name__ == "__main__":
    # Test için örnek bir veri bilimi profil girdisi:
    sample_profile = "Python, SQL, Machine Learning, PostgreSQL, Pandas, Data Analysis, Docker"
    recommend_jobs(sample_profile, top_n=5)