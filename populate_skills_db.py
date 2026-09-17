import psycopg2
from psycopg2.extras import execute_values
import json
from extract_skills import SKILL_DICTIONARY

def populate_database():
    print("🚀 Yetenek Entegrasyonu Başlatılıyor...\n")
    
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    cursor = conn.cursor()

    # 1. Adım: Benzersiz yetenekleri 'skills' tablosuna yükleme
    print("📥 1. Adım: 'skills' tablosu besleniyor...")
    skill_records = [(skill,) for skill in sorted(SKILL_DICTIONARY)]
    
    # skills tablosuna toplu ekleme (mükerrerliği önlemek için ON CONFLICT)
    insert_skills_query = """
        INSERT INTO skills (skill_name)
        VALUES %s
        ON CONFLICT (skill_name) DO NOTHING;
    """
    execute_values(cursor, insert_skills_query, skill_records)
    conn.commit()
    print(f"   -> {len(skill_records)} teknik yetenek 'skills' tablosuna yazıldı.")

    # 2. Adım: skill_name -> skill_id haritasını bellek içine alma
    cursor.execute("SELECT skill_id, skill_name FROM skills;")
    skill_map = {name: s_id for s_id, name in cursor.fetchall()}

    # 3. Adım: JSON dosyasını okuyup köprü tablosu (job_skills) kayıtlarını hazırlama
    print("\n🔗 2. Adım: 'job_skills' köprü tablosu kayıtları hazırlanıyor...")
    with open("jobs_extracted_skills.json", "r", encoding="utf-8") as f:
        job_data = json.load(f)

    bridge_records = []
    for item in job_data:
        j_id = item["job_id"]
        for skill_name in item["extracted_skills"]:
            if skill_name in skill_map:
                s_id = skill_map[skill_name]
                bridge_records.append((j_id, s_id))

    print(f"   -> Toplam {len(bridge_records)} ilişki kaydı oluşturuldu.")

    # 4. Adım: job_skills tablosuna Bulk Insert
    print("\n📤 3. Adım: 'job_skills' tablosuna toplu aktarım yapılıyor...")
    insert_bridge_query = """
        INSERT INTO job_skills (job_id, skill_id)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cursor, insert_bridge_query, bridge_records)
    conn.commit()
    print("✅ Başarılı! Köprü tablo ilişkileri kaydedildi.")

    cursor.close()
    conn.close()
    print("🔒 Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    populate_database()