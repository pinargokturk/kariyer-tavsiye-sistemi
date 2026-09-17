import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

# Çıktı klasörünü kontrol et
os.makedirs("staj_kanitlari", exist_ok=True)

def fetch_eda_data():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="staj123"
    )
    
    # 1. En çok talep edilen ilk 15 yetenek
    query_skills = """
        SELECT s.skill_name, COUNT(js.job_id) AS demand_count
        FROM skills s
        JOIN job_skills js ON s.skill_id = js.skill_id
        GROUP BY s.skill_name
        ORDER BY demand_count DESC
        LIMIT 15;
    """
    df_skills = pd.read_sql(query_skills, conn)
    
    # 2. İlan açıklamalarından rastgele 300 örnek metin (Kelime bulutu için)
    query_text = "SELECT description FROM job_postings LIMIT 300;"
    df_text = pd.read_sql(query_text, conn)
    
    conn.close()
    return df_skills, df_text

def plot_top_skills(df_skills):
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x="demand_count", 
        y="skill_name", 
        data=df_skills, 
        palette="viridis", 
        hue="skill_name", 
        legend=False
    )
    plt.title("En Çok Talep Edilen İlk 15 Teknoloji & Yetenek", fontsize=14, fontweight="bold")
    plt.xlabel("İlan Sayısı (Talep Frekansı)", fontsize=11)
    plt.ylabel("Teknik Beceri", fontsize=11)
    plt.tight_layout()
    save_path = "staj_kanitlari/eda_top_15_skills.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"📊 Yetenek çubuk grafiği kaydedildi: {save_path}")

def plot_wordcloud(df_text):
    full_text = " ".join(df_text['description'].dropna().tolist())
    
    wordcloud = WordCloud(
        width=1000, 
        height=500, 
        background_color="white", 
        colormap="magma",
        max_words=100
    ).generate(full_text)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    save_path = "staj_kanitlari/eda_wordcloud.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"☁️ Kelime bulutu kaydedildi: {save_path}")

if __name__ == "__main__":
    print("🚀 Keşifsel Veri Analizi (EDA) başlatılıyor...")
    df_skills, df_text = fetch_eda_data()
    plot_top_skills(df_skills)
    plot_wordcloud(df_text)
    print("✅ Tüm EDA grafikleri 'staj_kanitlari' klasörüne aktarıldı!")