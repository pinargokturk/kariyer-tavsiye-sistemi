import re
import json
import psycopg2
import pandas as pd

# 1. Genişletilmiş ve Varyasyon Haritalı Teknik Yetenek Havuzu
EXPANDED_SKILL_MAP = {
    # Diller
    "python": [r"\bpython\b"],
    "r": [r"\b[rR]\b"],  # Sadece tek başına duran R harfi
    "sql": [r"\bsql\b"],
    "c++": [r"\bc\+\+\b", r"\bcpp\b"],
    "c#": [r"\bc#\b", r"\bcsharp\b"],
    "c": [r"\b[cC]\b"],
    "java": [r"\bjava\b"],
    "scala": [r"\bscala\b"],
    "julia": [r"\bjulia\b"],
    "matlab": [r"\bmatlab\b"],
    "go": [r"\bgo\b", r"\bgolang\b"],
    "javascript": [r"\bjavascript\b", r"\bjs\b"],
    "typescript": [r"\btypescript\b", r"\bts\b"],
    "bash": [r"\bbash\b", r"\bshell\b"],
    
    # Veri & Makine Öğrenmesi Kütüphaneleri
    "pandas": [r"\bpandas\b"],
    "numpy": [r"\bnumpy\b"],
    "scipy": [r"\bscipy\b"],
    "scikit-learn": [r"\bscikit-learn\b", r"\bsci-kit learn\b", r"\bsklearn\b"],
    "tensorflow": [r"\btensorflow\b", r"\btf\b"],
    "keras": [r"\bkeras\b"],
    "pytorch": [r"\bpytorch\b", r"\btorch\b"],
    "xgboost": [r"\bxgboost\b"],
    "lightgbm": [r"\blightgbm\b"],
    "catboost": [r"\bcatboost\b"],
    "statsmodels": [r"\bstatsmodels\b"],
    "opencv": [r"\bopencv\b"],
    
    # NLP & LLM
    "nlp": [r"\bnlp\b", r"\bnatural language processing\b"],
    "nltk": [r"\bnltk\b"],
    "spacy": [r"\bspacy\b"],
    "bert": [r"\bbert\b"],
    "transformers": [r"\btransformers\b"],
    "llm": [r"\bllm\b", r"\blarge language models?\b"],
    "huggingface": [r"\bhuggingface\b", r"\bhugging face\b"],
    "gensim": [r"\bgensim\b"],
    
    # Büyük Veri & Veri Tabanı
    "spark": [r"\bspark\b", r"\bpyspark\b"],
    "hadoop": [r"\bhadoop\b"],
    "hive": [r"\bhive\b"],
    "kafka": [r"\bkafka\b"],
    "postgresql": [r"\bpostgresql\b", r"\bpostgres\b"],
    "mysql": [r"\bmysql\b"],
    "mongodb": [r"\bmongodb\b", r"\bmongo\b"],
    "redis": [r"\bredis\b"],
    "elasticsearch": [r"\belasticsearch\b"],
    "cassandra": [r"\bcassandra\b"],
    "snowflake": [r"\bsnowflake\b"],
    "bigquery": [r"\bbigquery\b"],
    "redshift": [r"\bredshift\b"],
    "sqlite": [r"\bsqlite\b"],
    
    # Bulut, MLOps, DevOps & Araçlar
    "aws": [r"\baws\b", r"\bamazon web services\b"],
    "azure": [r"\bazure\b"],
    "gcp": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "docker": [r"\bdocker\b"],
    "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "git": [r"\bgit\b"],
    "github": [r"\bgithub\b"],
    "gitlab": [r"\bgitlab\b"],
    "ci/cd": [r"\bci/cd\b", r"\bcicd\b"],
    "airflow": [r"\bairflow\b"],
    "mlflow": [r"\bmlflow\b"],
    "linux": [r"\blinux\b"],
    "postman": [r"\bpostman\b"],
    "rest api": [r"\brest api\b", r"\brestful\b", r"\bapi\b"],
    "flask": [r"\bflask\b"],
    "fastapi": [r"\bfastapi\b"],
    "django": [r"\bdjango\b"],
    "streamlit": [r"\bstreamlit\b"],
    "oop": [r"\boop\b", r"\bobject oriented programming\b"],

    # BI & Görselleştirme
    "tableau": [r"\btableau\b"],
    "power bi": [r"\bpower bi\b", r"\bpowerbi\b"],
    "excel": [r"\bexcel\b"],
    "matplotlib": [r"\bmatplotlib\b"],
    "seaborn": [r"\bseaborn\b"],
    "plotly": [r"\bplotly\b"],
    "looker": [r"\blooker\b"],
    "d3.js": [r"\bd3\.js\b", r"\bd3\b"],

    # Kavramlar & Metotlar
    "deep learning": [r"\bdeep learning\b", r"\bdl\b"],
    "machine learning": [r"\bmachine learning\b", r"\bml\b"],
    "data mining": [r"\bdata mining\b"],
    "computer vision": [r"\bcomputer vision\b"],
    "a/b testing": [r"\ba/b testing\b", r"\bab testing\b"],
    "statistics": [r"\bstatistics\b", r"\bstatistical\b"],
    "data analysis": [r"\bdata analysis\b", r"\bdata analytics\b"],
    "time series": [r"\btime series\b"],
    "etl": [r"\betl\b"],
    "data warehouse": [r"\bdata warehouse\b", r"\bdwh\b"]
}

SKILL_DICTIONARY = sorted(list(EXPANDED_SKILL_MAP.keys()))

def extract_skills_from_text(text, skill_dict=None):
    """
    Regex sınırları (\b) ve varyasyon haritası kullanarak 
    metinden kesin yetenek çıkarımı yapar.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    
    found_skills = set()
    
    for canonical_name, patterns in EXPANDED_SKILL_MAP.items():
        for pattern in patterns:
            flags = 0 if canonical_name in ["r", "c"] else re.IGNORECASE
            if re.search(pattern, text, flags):
                found_skills.add(canonical_name)
                break
                
    return sorted(list(found_skills))

def run_skill_extraction():
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

    print("\n🔍 2. Adım: Gelişmiş kural tabanlı yetenek çıkarımı yapılıyor...")
    df['extracted_skills'] = df['description'].apply(extract_skills_from_text)
    df['skill_count'] = df['extracted_skills'].apply(len)

    print("\n✅ Çıkarım Tamamlandı! Örnek İlanlar:\n")
    for _, row in df.head(3).iterrows():
        print(f"📌 [ID: {row['job_id']}] {row['title']}")
        print(f"   Bulunan Beceriler ({row['skill_count']} adet): {row['extracted_skills']}\n")

    df[['job_id', 'extracted_skills']].to_json("jobs_extracted_skills.json", orient="records", indent=2)
    print("💾 Çıkarılan yetenekler 'jobs_extracted_skills.json' dosyasına güncellendi.")

if __name__ == "__main__":
    run_skill_extraction()