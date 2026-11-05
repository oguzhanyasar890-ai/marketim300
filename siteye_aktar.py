import sqlite3, json

baglanti = sqlite3.connect('marketim3000.db')
baglanti.row_factory = sqlite3.Row
imlec = baglanti.cursor()

# 1. Tablo yoksa otomatik oluştur
imlec.execute("""
CREATE TABLE IF NOT EXISTS kitaplar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik TEXT NOT NULL,
    yazar TEXT DEFAULT 'Oğuzhan Yaşar',
    kategori TEXT DEFAULT 'Genel',
    dosyaAdi TEXT NOT NULL,
    kapakUrl TEXT,
    aciklama TEXT,
    fiyat REAL DEFAULT 0,
    indirmeSayisi INTEGER DEFAULT 0,
    aktif INTEGER DEFAULT 1,
    tarih DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. Tablo boşsa başlangıç kitaplarını otomatik ekle
imlec.execute("SELECT COUNT(*) FROM kitaplar")
if imlec.fetchone()[0] == 0:
    imlec.executemany("""
    INSERT INTO kitaplar (baslik, yazar, kategori, dosyaAdi, kapakUrl, aciklama, fiyat, indirmeSayisi)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ('Sıfırdan Yapay Zeka Kullanım Rehberi', 'Oğuzhan Yaşar', 'Teknoloji', 'yapay-zeka.pdf', 'https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=800', 'Adım adım yapay zeka araçlarını ve etkili komut yazma tekniklerini öğrenin.', 149.90, 12),
        ('Sıfırdan Bütçe Yönetimi ve Finansal Özgürlük Rehberi', 'Oğuzhan Yaşar', 'Finans', 'butce-yonetimi.pdf', 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?q=80&w=800', 'Gelir-gider dengesi kurma, birikim ve finansal özgürlüğe ulaşma kılavuzu.', 129.90, 8)
    ])
    baglanti.commit()

# 3. Verileri çek ve urunler.json dosyasına aktar
imlec.execute("SELECT id, baslik, yazar, kategori, dosyaAdi, kapakUrl, aciklama, fiyat, indirmeSayisi FROM kitaplar WHERE aktif = 1 ORDER BY id DESC")
kitaplar = []
for satir in imlec.fetchall():
    k = dict(satir)
    k['id'] = f"sql_{k['id']}"
    kitaplar.append(k)

with open('urunler.json', 'w', encoding='utf-8') as f:
    json.dump(kitaplar, f, ensure_ascii=False, indent=2)

print(f"Başarılı! {len(kitaplar)} kitap urunler.json dosyasına aktarıldı.")
baglanti.close()
