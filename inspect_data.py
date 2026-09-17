import pandas as pd

# CSV dosyasını okuyoruz
df = pd.read_csv("jobs_raw.csv")

print("✅ CSV Dosyası Başarıyla Okundu!")
print(f"📊 Toplam Satır Sayısı: {len(df)}")
print("\n📌 Mevcut Kolonlar:")
print(df.columns.tolist())

print("\n🔍 İlk 2 Satır Örneği:")
print(df.head(2))
