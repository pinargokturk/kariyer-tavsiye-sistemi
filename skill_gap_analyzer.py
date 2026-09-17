import psycopg2
from recommendation_engine import recommend_jobs
from extract_skills import extract_skills_from_text, SKILL_DICTIONARY

def get_required_skills_for_job(job_id):
    """İlişkisel veritabanından ilanın gerektirdiği teknik yetenekleri çeker."""
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    cursor = conn.cursor()
    query = """
        SELECT s.skill_name
        FROM skills s
        JOIN job_skills js ON s.skill_id = js.skill_id
        WHERE js.job_id = %s;
    """
    cursor.execute(query, (int(job_id),))
    skills = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return set(skills)

def analyze_skill_gap(user_profile_text, top_n=3):
    print("=" * 75)
    print("🚀 KARİYER AÇIĞI (SKILL GAP) VE UYUM ANALİZİ")
    print("=" * 75)
    
    # 1. Kullanıcının sahip olduğu yetenekleri ayıkla
    user_skills = set(extract_skills_from_text(user_profile_text, SKILL_DICTIONARY))
    print(f"👤 Adayın Tespit Edilen Yetenekleri ({len(user_skills)} adet):")
    print(f"   {sorted(list(user_skills))}\n")
    
    # 2. Tavsiye motorundan en uygun ilk N ilanı getir
    recommendations = recommend_jobs(user_profile_text, top_n=top_n)
    
    print("\n" + "=" * 75)
    print("📊 POZİSYON BAZLI YETENEK AÇIĞI RAPORU")
    print("=" * 75)
    
    for rank, (job_id, title, score) in enumerate(recommendations, 1):
        job_skills = get_required_skills_for_job(job_id)
        
        # Küme Teorisi İşlemleri:
        matched_skills = user_skills.intersection(job_skills)
        missing_skills = job_skills.difference(user_skills)
        
        # Yetenek Kapsama Oranı (Skill Match Ratio)
        coverage_ratio = (len(matched_skills) / len(job_skills) * 100) if job_skills else 100.0
        
        print(f"\n[{rank}] İlan ID: {job_id} | {title}")
        print(f"   🔹 Kosinüs Benzerlik Skoru : %{score * 100:.2f}")
        print(f"   🔹 İlanın Aradığı Beceriler : {sorted(list(job_skills))}")
        print(f"   ✅ Eşleşen Beceriler       : {sorted(list(matched_skills)) if matched_skills else 'Yok'}")
        print(f"   ⚠️  EKSİK Beceriler (Skill Gap): {sorted(list(missing_skills)) if missing_skills else 'Tüm gereksinimler karşılanıyor!'}")
        print(f"   🎯 Yetenek Kapsama Oranı    : %{coverage_ratio:.1f}")

if __name__ == "__main__":
    # Örnek Kullanıcı Profili (Örn: Veri analitiği ve temel Python bilen bir profil)
    sample_candidate = "I know Python, SQL, Pandas, and Data Analysis. I do data mining and statistical modeling."
    analyze_skill_gap(sample_candidate, top_n=3)