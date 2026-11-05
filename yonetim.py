import sqlite3, json, os, subprocess

DB_PATH = 'marketim3000.db'
JSON_PATH = 'urunler.json'

def baglan():
    b = sqlite3.connect(DB_PATH)
    b.row_factory = sqlite3.Row
    b.execute("""
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
    return b

def json_guncelle():
    b = baglan()
    imlec = b.cursor()
    imlec.execute("SELECT id, baslik, yazar, kategori, dosyaAdi, kapakUrl, aciklama, fiyat, indirmeSayisi FROM kitaplar WHERE aktif = 1 ORDER BY id DESC")
    kitaplar = []
    for satir in imlec.fetchall():
        k = dict(satir)
        k['id'] = f"sql_{k['id']}"
        kitaplar.append(k)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(kitaplar, f, ensure_ascii=False, indent=2)
    b.close()
    print(f"\n[✓] urunler.json güncellendi! (Toplam {len(kitaplar)} aktif kitap)")

def kitaplari_listele():
    b = baglan()
    imlec = b.cursor()
    imlec.execute("SELECT id, baslik, kategori, fiyat, dosyaAdi FROM kitaplar WHERE aktif = 1 ORDER BY id ASC")
    rows = imlec.fetchall()
    print("\n--- MEVCUT KİTAPLAR ---")
    if not rows:
        print("Henüz kayıtlı kitap yok.")
    for r in rows:
        fiyat_str = f"{r['fiyat']} TL" if r['fiyat'] > 0 else "Ücretsiz"
        print(f"[{r['id']}] {r['baslik']} | {r['kategori']} | {fiyat_str} | Dosya: {r['dosyaAdi']}")
    b.close()

def kitap_ekle():
    print("\n--- YENİ KİTAP EKLE ---")
    baslik = input("Kitap Adı: ").strip()
    if not baslik: return
    yazar = input("Yazar (Varsayılan: Oğuzhan Yaşar): ").strip() or "Oğuzhan Yaşar"
    kategori = input("Kategori (Teknoloji/Finans/Roman vb.): ").strip() or "Genel"
    dosyaAdi = input("Dosya Adı (Örn: kitap.pdf veya kitap.txt): ").strip()
    kapakUrl = input("Kapak Resmi URL veya Yolu: ").strip() or "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=800"
    aciklama = input("Kısa Açıklama: ").strip()
    fiyat_girdi = input("Fiyat TL (Ücretsiz için 0 yazın): ").strip()
    try:
        fiyat = float(fiyat_girdi.replace(',', '.')) if fiyat_girdi else 0.0
    except:
        fiyat = 0.0

    b = baglan()
    b.execute("INSERT INTO kitaplar (baslik, yazar, kategori, dosyaAdi, kapakUrl, aciklama, fiyat) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (baslik, yazar, kategori, dosyaAdi, kapakUrl, aciklama, fiyat))
    b.commit()
    b.close()
    print(f"\n[+] '{baslik}' veri tabanına eklendi!")
    json_guncelle()

def fiyat_guncelle():
    kitaplari_listele()
    secim = input("\nFiyatını değiştirmek istediğiniz kitabın [ID] numarası: ").strip()
    if not secim.isdigit(): return
    yeni_fiyat = input("Yeni Fiyat (TL): ").strip()
    try:
        fiyat = float(yeni_fiyat.replace(',', '.'))
        b = baglan()
        b.execute("UPDATE kitaplar SET fiyat = ? WHERE id = ?", (fiyat, int(secim)))
        b.commit()
        b.close()
        print("\n[✓] Fiyat güncellendi!")
        json_guncelle()
    except:
        print("\n[!] Geçersiz fiyat girdiniz.")

def kitap_sil():
    kitaplari_listele()
    secim = input("\nSilmek (yayından kaldırmak) istediğiniz kitabın [ID] numarası: ").strip()
    if not secim.isdigit(): return
    b = baglan()
    b.execute("UPDATE kitaplar SET aktif = 0 WHERE id = ?", (int(secim),))
    b.commit()
    b.close()
    print("\n[-] Kitap yayından kaldırıldı.")
    json_guncelle()

def github_gonder():
    json_guncelle()
    if not os.path.exists('.git'):
        print("\n[!] Bu klasör henüz GitHub deponuza bağlanmamış.")
        repo = input("GitHub Repo Adresiniz (Örn: https://github.com/kullaniciadi/repo.git): ").strip()
        if not repo: return
        os.system("git init && git branch -M main")
        os.system(f"git remote add origin {repo}")
    
    os.system('git config user.name "Oğuzhan Yaşar"')
    os.system('git config user.email "oguzhanyasar890@gmail.com"')
    os.system("git add urunler.json index.html *.pdf *.epub *.txt 2>/dev/null")
    os.system('git commit -m "Veri tabanı ve katalog güncellendi"')
    print("\n[↑] Değişiklikler GitHub'a gönderiliyor...")
    sonuc = os.system("git push -u origin main")
    if sonuc == 0:
        print("\n[✓] Başarılı! Siteniz (marketim3000.online) birkaç dakika içinde güncellenecektir.")
    else:
        print("\n[!] Gönderim sırasında hata oluştu. GitHub Token veya depo adresinizi kontrol edin.")

def menu():
    while True:
        print("\n====================================")
        print("   MARKETİM3000 YÖNETİM & YAYIN     ")
        print("====================================")
        print("1) Kitapları Listele")
        print("2) Yeni Kitap Ekle")
        print("3) Kitap Fiyatı Güncelle")
        print("4) Kitap Sil (Yayından Kaldır)")
        print("5) Siteyi Canlıya Gönder (GitHub Push)")
        print("6) Çıkış")
        secim = input("Seçiminiz (1-6): ").strip()
        
        if secim == '1': kitaplari_listele()
        elif secim == '2': kitap_ekle()
        elif secim == '3': fiyat_guncelle()
        elif secim == '4': kitap_sil()
        elif secim == '5': github_gonder()
        elif secim == '6': break
        else: print("Geçersiz seçim, tekrar deneyin.")

if __name__ == '__main__':
    menu()
