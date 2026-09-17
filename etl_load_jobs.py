import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

def run_etl():
    print("🚀 ETL Pipeline Başlatılıyor...\n")
    
    # 1. EXTRACT: Ham CSV verisini okuma
    print("📥 1. Adım: Ham CSV verisi okunuyor...")
    df = pd.read_csv("jobs_raw.csv")
    print(f"   -> Ham veri boyutu: {len(df)} satır, {len(df.columns)} sütun")

    # 2. TRANSFORM: Veriyi filtreleme ve hazırlama
    print("⚙️  2. Adım: Veri temizleme ve dönüştürme yapılıyor...")
    
    # İhtiyacımız olan 4 sütunu seçiyoruz
    target_columns = {
        'Job Title': 'title',
        'Company Name': 'company',
        'Location': 'location',
        'Job Description': 'description'
    }
    
    df_clean = df[list(target_columns.keys())].copy()
    
    # Sütun isimlerini veritabanı şemamıza uygun hale getiriyoruz
    df_clean.rename(columns=target_columns, inplace=True)
    
    # Başlığı veya Açıklaması boş olan satırları eliyoruz (model için kritik)
    df_clean.dropna(subset=['title', 'description'], inplace=True)
    
    # Metin içindeki fazla boşlukları temizleyelim ve şirket/konum boşsa 'Belirtilmemiş' yazalım
    df_clean['company'] = df_clean['company'].fillna('Belirtilmemiş')
    df_clean['location'] = df_clean['location'].fillna('Belirtilmemiş')
    
    # Mükerrer (birebir aynı ilan başlığı ve açıklaması olan) kayıtları düşürelim
    df_clean.drop_duplicates(subset=['title', 'description'], inplace=True)
    
    print(f"   -> Temizleme sonrası aktarıma hazır kayıt sayısı: {len(df_clean)}")

    # 3. LOAD: PostgreSQL'e Toplu Yükleme (Bulk Insert)
    print("📤 3. Adım: PostgreSQL veritabanına toplu aktarım başlatılıyor...")
    
    # Tuple listesi haline getiriyoruz
    records_to_insert = [
        (row['title'], row['company'], row['location'], row['description'])
        for _, row in df_clean.iterrows()
    ]
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="staj123"
        )
        cursor = conn.cursor()
        
        # Olası eski veriyi temizleyelim (sıfırdan tertemiz yükleme)
        cursor.execute("TRUNCATE TABLE job_skills, skills, job_postings RESTART IDENTITY CASCADE;")
        
        # Bulk Insert SQL sorgusu
        insert_query = """
            INSERT INTO job_postings (title, company, location, description)
            VALUES %s;
        """
        
        # Binlerce satırı tek seferde hızlıca yazar
        execute_values(cursor, insert_query, records_to_insert)
        
        conn.commit()
        print(f"✅ Başarılı! Toplam {len(records_to_insert)} ilan 'job_postings' tablosuna aktarıldı.")
        
        cursor.close()
        conn.close()
        print("🔒 Veritabanı bağlantısı kapatıldı.")

    except Exception as e:
        print(f"❌ Aktarım sırasında hata oluştu: {e}")

if __name__ == "__main__":
    run_etl()
    