import psycopg2

def test_connection():
    try:
        # PostgreSQL bağlantı bilgileri
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="staj123"
        )
        cursor = connection.cursor()
        
        # PostgreSQL sürümünü sorguluyoruz
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("✅ Bağlantı Başarılı!")
        print(f"📊 PostgreSQL Sürümü: {db_version[0]}")
        
        # Dün oluşturduğumuz tabloları kontrol edelim
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print("\n📁 Veritabanında Tespit Edilen Tablolar:")
        for t in tables:
            print(f" - {t[0]}")
            
        cursor.close()
        connection.close()
        print("\n🔒 Bağlantı güvenli bir şekilde kapatıldı.")

    except Exception as error:
        print(f"❌ Bağlantı Hatası: {error}")

if __name__ == "__main__":
    test_connection()