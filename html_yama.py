import os

dosya = 'index.html'
if not os.path.exists(dosya):
    print("[!] index.html bu klasörde bulunamadı. Lütfen index.html dosyanızı /root/marketim3000 klasörüne kopyalayın.")
    exit()

with open(dosya, 'r', encoding='utf-8') as f:
    kod = f.read()

# 1. modalAuthor span hatasını düzelt
kod = kod.replace("document.getElementById('modalAuthor').querySelector('span').innerText = book.yazar;", "document.getElementById('modalAuthor').innerText = book.yazar;")

# 2. loadBooks fonksiyonunu urunler.json okuyacak şekilde güncelle
eski_load = """async function loadBooks() {
  try {
    const querySnapshot = await getDocs(collection(db, "kitaplar"));
    allBooks = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));"""

yeni_load = """async function loadBooks() {
  try {
    let localBooks = [];
    try {
      const res = await fetch('urunler.json?v=' + Date.now(), { cache: 'no-store' });
      if (res.ok) localBooks = await res.json();
    } catch (e) {}
    let fbBooks = [];
    try {
      const querySnapshot = await getDocs(collection(db, "kitaplar"));
      fbBooks = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (e) {}
    const localTitles = new Set(localBooks.map(b => (b.baslik || '').toLowerCase()));
    allBooks = [...localBooks, ...fbBooks.filter(b => !localTitles.has((b.baslik || '').toLowerCase()))];"""

if eski_load in kod:
    kod = kod.replace(eski_load, yeni_load)
    with open(dosya, 'w', encoding='utf-8') as f:
        f.write(kod)
    print("[✓] index.html başarıyla SQLite (urunler.json) ile entegre edildi!")
else:
    print("[i] index.html zaten güncel veya farklı bir yapıda.")
