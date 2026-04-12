import scraper
import db_manager

print("=== PENGUJIAN INTEGRASI BACKEND ===")

# 1. Siapkan 'Wadah' Database
print("\n1. Menyiapkan Database...")
db_manager.init_db()

# 2. Ambil Data dari Internet
print("\n2. Menjalankan Scraper...")
base_url = "https://www.polban.ac.id/category/kemahasiswaan/event/"
html_mentah = scraper.fetch_html(base_url)

if html_mentah:
    # 3. Ekstrak menjadi List of Dictionaries
    hasil_data = scraper.parse_events(html_mentah)
    print(f"Berhasil mengekstrak {len(hasil_data)} acara.")

    # 4. Masukkan ke Database satu per satu
    print("\n3. Memasukkan data ke SQLite...")
    for data in hasil_data:
        db_manager.upsert_event(data)
        print(f"✔️ Tersimpan: {data['nama_event']}")

    # 5. Buktikan data benar-benar masuk
    print("\n4. Cek Hasil Akhir di Database:")
    data_db = db_manager.get_all_events()
    print(f"Total data di database saat ini: {len(data_db)} baris.")

    print("\n--- STATUS: PROTOTIPE BERHASIL! ---")
else:
    print("\nGagal mengambil HTML, silakan cek koneksi internet.")