#  AI Destekli Akıllı Kariyer & İş Tavsiye Portalı

Bu proje; veri bilimi, makine öğrenmesi ve veri analitiği alanındaki binlerce iş ilanını doğal dil işleme (NLP) ve bilgi erişimi (Information Retrieval) teknikleriyle analiz eden, adayların yüklediği PDF özgeçmişleri değerlendirerek en uygun pozisyonları sıralayan ve adaya özel **Kariyer Açığı (Skill Gap)** analizi sunan uçtan uca bir veri mühendisliği ve yapay zeka sistemidir.

---

## Öne Çıkan Özellikler

- **Dinamik PDF CV Analizi:** Adayın yüklediği PDF özgeçmişi `pypdf` ile ayrıştırılır, metin ön işleme filtrelerinden geçirilir ve profil yetenekleri kural tabanlı olarak çıkarılır.
- **TF-IDF & Kosinüs Benzerliği Sıralaması:** 3.699 iş ilanı ile aday profili 5.000 boyutlu n-gram (1, 2) vektör uzayına projekte edilerek en uygun pozisyonlar milisaniyeler içinde derecelendirilir.
- **Kümeler Teorisi Tabanlı Yetenek Açığı (Skill Gap):** İlanın gerektirdiği teknik gereksinimler ile adayın yetenekleri arasındaki küme farkı (B \ A) hesaplanarak adaya eksik teknolojiler ve yetenek karşılama yüzdesi sunulur.
- **Piyasa Analitiği Gösterge Paneli:** En çok talep edilen ilk 15 teknoloji çubuk grafiği ve sektör kelime bulutu (WordCloud) ile veri bilimi ekosisteminin güncel profilini görselleştirir.
- **Düşük Gecikme (Low-Latency Inference):** 3.699 ilan üzerinde yapılan çıkarım ve sıralama testlerinde ortalama **~26.72 ms** arama süresi.

---

## Mimari & Teknoloji Yığını

| Katman | Teknolojiler | Açıklama |
| :--- | :--- | :--- |
| **Veritabanı (RDBMS)** | Docker, PostgreSQL 15, DBeaver | 3NF şeması (`job_postings`, `skills`, `job_skills`), Many-to-Many köprü tablosu, B-Tree indeksleme. |
| **Veri Mühendisliği & ETL** | Python, `pandas`, `psycopg2` | 3.909 ham ilandan 3.699 temiz ilana indirgeme, `execute_values` ile toplu aktarım (Bulk Insert). |
| **Doğal Dil İşleme (NLP)** | `nltk`, `re` (Regex) | Stop-words eliminasyonu, küçük harf normalizasyonu, noktalama temizliği, 140+ terimlik genişletilmiş varlık eşleme havuzu (`EXPANDED_SKILL_MAP`). |
| **Makine Öğrenmesi** | `scikit-learn`, `numpy` | `TfidfVectorizer` (`max_features=5000`, `min_df=2`, `ngram_range=(1,2)`), Kosinüs Benzerliği (Cosine Similarity). |
| **Web UI & Dashboard** | `streamlit`, `pypdf`, `matplotlib`, `seaborn`, `wordcloud` | Çok sekmeli kullanıcı arayüzü, PDF yükleyici, interaktif metrik kartları ve EDA panelleri. |

---

## Proje Dizin Yapısı

kariyer_tavsiye_sistemi/
├── app.py                     # Streamlit çok sekmeli web uygulaması
├── nlp_preprocessing.py        # Metin temizleme ve normalizasyon modülü
├── extract_skills.py           # Genişletilmiş kural tabanlı teknik yetenek çıkarıcı (140+ Terim)
├── tfidf_vectorizer.py         # TF-IDF model eğitimi ve serileştirme (.pkl)
├── recommendation_engine.py    # Kosinüs benzerliği tabanlı tavsiye motoru
├── skill_gap_analyzer.py       # Küme teorisi tabanlı eksik yetenek analizi
├── eda_visualization.py        # Çubuk grafik ve kelime bulutu üreten EDA betiği
├── run_system_tests.py         # Uç durumlar, stres ve gecikme (latency) testleri
├── requirements.txt            # Proje bağımlılıkları
├── tfidf_vectorizer.pkl        # Eğitilmiş TF-IDF modeli
├── tfidf_matrix.pkl            # 3.699 ilanın seyrek öznitelik matrisi
├── jobs_metadata.pkl           # Hızlı erişim için ilan metaverileri
├── staj_kanitlari/             # EDA görselleri ve sistem test ekran çıktıları
│   ├── eda_top_15_skills.png
│   ├── eda_wordcloud.png
│   └── gun14_sistem_testleri_latency.png
└── README.md                   # Proje dokümantasyonu

---

## Kurulum ve Çalıştırma Adımları

1. Depoyu Klonlayın ve Sanal Ortamı Başlatın
   git clone [https://github.com/kullaniciadi/kariyer-tavsiye-sistemi.git](https://github.com/kullaniciadi/kariyer-tavsiye-sistemi.git)
   cd kariyer-tavsiye-sistemi
   python -m venv venv
   Windows: venv\Scripts\activate
   Linux/macOS: source venv/bin/activate
   pip install -r requirements.txt

2. Docker ile PostgreSQL Veritabanını Başlatın
   docker run --name kariyer-postgres -e POSTGRES_PASSWORD=staj123 -p 5432:5432 -d postgres

3. Modelleri ve Vektör Matrisini Üretin
   python tfidf_vectorizer.py
   python eda_visualization.py

4. Web Portalını Başlatın
   streamlit run app.py
   (Uygulama tarayıcınızda http://localhost:8501 adresinde açılacaktır.)

---

## Sistem Doğrulama ve Performans Testleri

Sistemin uç durum (edge case) toleransı ve çıkarım hızını doğrulamak için:
python run_system_tests.py

- **Veritabanı İndeksleme Başarısı:** B-Tree indeksleme ile unvan bazlı SQL arama süreleri 3.351 ms'den 0.49 ms seviyesine düşürülmüştür.
- **Model Çıkarım Gecikmesi:** 3.699 ilan üzerinde aday profili eşleştirmesi ortalama 26.72 ms sürmektedir.
- **Hata Yönetimi:** Özel karakterler, boş girdiler ve veri tabanı tip uyumsuzlukları (numpy.int64 / psycopg2) zarifçe yakalanarak kullanıcıya geribildirim verilmektedir.