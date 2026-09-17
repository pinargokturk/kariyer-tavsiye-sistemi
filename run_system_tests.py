import time
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from nlp_preprocessing import clean_text
from extract_skills import extract_skills_from_text, SKILL_DICTIONARY

def load_resources():
    with open("tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open("jobs_metadata.pkl", "rb") as f:
        jobs_df = pickle.load(f)
    return vectorizer, tfidf_matrix, jobs_df

def evaluate_test_cases():
    print("=" * 75)
    print("🧪 SİSTEM DOĞRULAMA, UÇ DURUM (EDGE CASE) VE PERFORMANS TESTLERİ")
    print("=" * 75)

    vectorizer, tfidf_matrix, jobs_df = load_resources()

    test_scenarios = [
        ("Normal Profil (Data Scientist)", "Experienced in Python, SQL, Machine Learning, Deep Learning, and Pandas."),
        ("Sınır Durum 1 (Tek Terim Girdisi)", "Python"),
        ("Sınır Durum 2 (Alakasız / Gürültülü Metin)", "!@#$%^&*() random non-technical text 123456"),
        ("Sınır Durum 3 (Farklı Alan - BI / Analist)", "Power BI, Tableau, Excel, Business Intelligence, Reporting, Dashboards"),
        ("Sınır Durum 4 (Boş Girdi Simülasyonu)", "   ")
    ]

    latencies = []

    for name, input_text in test_scenarios:
        print(f"\n▶️ Test Senaryosu: {name}")
        print(f"   Girdi: '{input_text}'")

        start_time = time.perf_counter()

        try:
            # Boşluk kontrolü
            if not input_text.strip():
                print("   ⚠️ Uyarı Yakalandı: Boş girdi tespit edildi, model tetiklenmedi.")
                continue

            # Yetenek çıkarımı
            skills = extract_skills_from_text(input_text, SKILL_DICTIONARY)
            
            # NLP temizleme ve vektör dönüşümü
            cleaned = clean_text(input_text)
            user_vec = vectorizer.transform([cleaned])
            
            # Benzerlik hesaplama ve sıralama
            sims = cosine_similarity(user_vec, tfidf_matrix).flatten()
            top_idx = sims.argsort()[::-1][:3]

            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            latencies.append(elapsed_ms)

            max_score = sims[top_idx[0]] * 100
            best_match_title = jobs_df.iloc[top_idx[0]]['title']

            print(f"   Tespit Edilen Yetenekler : {skills if skills else 'Hiçbiri'}")
            print(f"   En Uyumlu Pozisyon       : {best_match_title} (Skor: %{max_score:.2f})")
            print(f"   Arama Gecikmesi (Latency): {elapsed_ms:.2f} ms")

        except Exception as e:
            print(f"   ❌ Beklenmeyen Hata: {str(e)}")

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print("\n" + "=" * 75)
        print(f"⚡ PERFORMANS ÖZETİ: Ortalama Yanıt Süresi = {avg_latency:.2f} ms")
        print("=" * 75)

if __name__ == "__main__":
    evaluate_test_cases()