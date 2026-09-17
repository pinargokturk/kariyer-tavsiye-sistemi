import re
import nltk
from nltk.corpus import stopwords
import pandas as pd
import psycopg2

# NLTK Stopwords veri tabanını indiriyoruz
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # 1. Küçük harfe dönüştürme
    text = text.lower()
    
    # 2. URL ve e-posta adreslerini temizleme
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # 3. HTML etiketlerini kaldırma
    text = re.sub(r'<.*?>', '', text)
    
    # 4. Sayıları ve alfasayısal olmayan özel sembolleri temizleme (C++, C# gibi diller için + ve # korunabilir veya kelime sınırları alınır)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # 5. Fazla boşlukları ve satır sonlarını tek boşluğa indirgeme
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 6. Stop-words (etkisiz kelimeler) temizliği
    tokens = text.split()
    filtered_tokens = [w for w in tokens if w not in stop_words and len(w) > 1]
    
    return " ".join(filtered_tokens)

def test_preprocessing():
    print("🚀 NLP Ön İşleme Test Ediliyor...\n")
    
    # PostgreSQL'den ilk 3 ilanın açıklamasını çekip test edelim
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    df = pd.read_sql("SELECT job_id, title, description FROM job_postings LIMIT 3;", conn)
    conn.close()
    
    for idx, row in df.iterrows():
        raw_desc = row['description']
        cleaned_desc = clean_text(raw_desc)
        
        print(f"📌 İlan ID: {row['job_id']} | Başlık: {row['title']}")
        print(f"🔹 Ham Metin İlk 120 Karakter   : {raw_desc[:120]}...")
        print(f"🔹 Temiz Metin İlk 120 Karakter : {cleaned_desc[:120]}...")
        print(f"📊 Kelime Sayısı Değişimi      : {len(raw_desc.split())} -> {len(cleaned_desc.split())}\n")

if __name__ == "__main__":
    test_preprocessing()