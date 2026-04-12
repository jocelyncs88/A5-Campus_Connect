import scraper
import db_manager

print("=== PENGUJIAN INTEGRASI BACKEND ===")

# 1. Siapkan 'Wadah' Database
print("\n1. Menyiapkan Database...")
db_manager.init_db()

# 2. Ambil Data dari Internet (hingga 100 event)
print("\n2. Menjalankan Scraper (target 100 data)...")
hasil_data = scraper.ambil_event_polban(limit=100)

if hasil_data:
    print(f"Berhasil mengekstrak {len(hasil_data)} acara.")

    # 3. Masukkan ke Database satu per satu
    print("\n3. Memasukkan data ke SQLite...")
    for data in hasil_data:
        db_manager.upsert_event(data)
        print(f"✔️ Tersimpan: {data['nama_event']}")

    # 4. Buktikan data benar-benar masuk
    print("\n4. Cek Hasil Akhir di Database:")
    data_db = db_manager.get_all_events()
    print(f"Total data di database saat ini: {len(data_db)} baris.")

    print("\n--- STATUS: PROTOTIPE BERHASIL! ---")
else:
    print("\nGagal mengambil data event, silakan cek koneksi internet / struktur website.")