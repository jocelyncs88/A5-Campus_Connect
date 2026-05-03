import requests
from bs4 import BeautifulSoup

# ==========================================
# FUNGSI 1: MENGAMBIL HTML
# ==========================================
def fetch_html(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        print(f"Mencoba menghubungi: {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        print("Berhasil terhubung! Sedang mengunduh HTML...")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ups, terjadi kesalahan saat menghubungi server: {e}")
        return None

# ==========================================
# FUNGSI 2: MEMBEDAH HTML (PARSING)
# ==========================================
def parse_events(html_content):
    """Mengekstrak data event dari HTML menggunakan BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    scraped_data_list = [] 

    # Wadah utama sesuai hasil inspect element
    event_containers = soup.find_all('div', class_='hs-post-wrapper')
    print(f"\nDitemukan {len(event_containers)} wadah event di halaman ini.")

    for container in event_containers:
        # 1. Ekstrak Judul
        title_tag = container.find('h3', class_='entry-title') 
        if title_tag:
            # Mengambil teks judul
            raw_title = title_tag.text.strip()
            # Mengambil atribut 'href' dari tag <a> di dalam judul
            a_tag = title_tag.find('a')
            event_link = a_tag.get('href') if a_tag else "Link Tidak Ditemukan"
        else:
            raw_title = "Judul Tidak Diketahui"
            event_link = "Link Tidak Ditemukan"

        # Memisahkan tanggal dan judul asli yang menyatu dalam satu teks
        if " : " in raw_title:
            # .split(" : ", 1) memotong teks maksimal 1 kali berdasarkan " : "
            # Hasilnya adalah List dengan 2 elemen: [Tanggal, Judul Asli]
            pecahan = raw_title.split(" : ", 1)
            tanggal_waktu = pecahan[0].strip()  # Bagian Kiri (Tanggal)
            nama_event = pecahan[1].strip()     # Bagian Kanan (Judul Bersih)
        else:
            # Fallback jika kebetulan ada postingan yang tidak pakai format titik dua
            tanggal_waktu = "TBA"
            nama_event = raw_title

        # 2. Ekstrak Gambar (Diperbarui untuk mengatasi Lazy Loading)
        figure_tag = container.find('figure', class_='entry-figure')
        img_tag = figure_tag.find('img') if figure_tag else None
        
        if img_tag:
            # Kita coba ambil dari 'data-lazy-src' atau 'data-src' dulu. Kalau ga ada, baru ambil 'src' biasa.
            gambar_poster = img_tag.get('data-lazy-src') or img_tag.get('data-src') or img_tag.get('src')
        else:
            gambar_poster = "Link_Gambar_Tidak_Ada"

        # 3. Ekstrak Deskripsi
        content_div = container.find('div', class_='entry-content')
        deskripsi_singkat = content_div.text.strip()[:70] + "..." if content_div else "Deskripsi tidak tersedia."

        # Generate ID unik
        event_id = "SCR-" + nama_event[:10].replace(" ", "").upper()

        # UPGRADE 1: Logika Klasifikasi Internal/External
        teks_penentu = (nama_event + " " + deskripsi_singkat).lower()
        if "polban" in teks_penentu or "hima" in teks_penentu or "mahasiswa" in teks_penentu:
            jenis_event = "Internal"
        else:
            jenis_event = "External"

        # UPGRADE 2: Ekstrak Kategori
        kategori_tag = container.find('div', class_='entry-categories')
        kategori = kategori_tag.text.strip() if kategori_tag else "Umum"

        # Bungkus ke dalam Dictionary
        event_data = {
            "event_id": event_id,
            "nama_event": nama_event,
            "deskripsi_singkat": deskripsi_singkat,
            "gambar_poster": gambar_poster,
            "jenis_event": jenis_event,
            "tanggal_waktu": tanggal_waktu,
            "source": event_link,
            "kategori": kategori
        }

        scraped_data_list.append(event_data)

    return scraped_data_list


def _event_identity(event):
    """Identitas event yang dipakai untuk mendeteksi duplikasi."""
    nama_event = (event.get("nama_event") or "").strip().lower()
    tanggal_waktu = (event.get("tanggal_waktu") or "").strip().lower()
    return nama_event, tanggal_waktu


def ambil_event_polban(limit=100, base_url="https://www.polban.ac.id/category/kemahasiswaan/event/", existing_keys=None):
    """Ambil event Polban lintas halaman sampai mencapai limit, data habis, atau ketemu event lama."""
    semua_event = []
    page = 1
    existing_keys = set(existing_keys or [])

    while len(semua_event) < limit:
        print(f"\n>>> SEDANG MEMPROSES HALAMAN {page} <<<")

        if page == 1:
            target_url = base_url
        else:
            target_url = f"{base_url}page/{page}/"

        html_mentah = fetch_html(target_url)
        if not html_mentah:
            print("Gagal mengambil halaman, proses dihentikan.")
            break

        hasil_per_halaman = parse_events(html_mentah)
        if not hasil_per_halaman:
            print("Tidak ada event lagi pada halaman ini, proses dihentikan.")
            break

        stop_scraping = False
        for event in hasil_per_halaman:
            event_key = _event_identity(event)

            # Begitu ketemu event yang sudah ada di DB, asumsi sisanya adalah data lama.
            if event_key in existing_keys:
                print(f"Event lama ditemukan: {event.get('nama_event')} - scraping dihentikan.")
                stop_scraping = True
                break

            semua_event.append(event)
            existing_keys.add(event_key)

            if len(semua_event) >= limit:
                break

        if stop_scraping:
            break

        page += 1

    return semua_event[:limit]

# ==========================================
# ENTRY POINT (TESTING)
# ==========================================
if __name__ == "__main__":
    base_url = "https://www.polban.ac.id/category/kemahasiswaan/event/"
    
    # KONSEP LECTURER: Penggunaan List utama untuk menampung gabungan data dari semua halaman
    semua_event = []
    
    # Targetkan 2 halaman saja dulu untuk MVP
    jumlah_halaman = 1 

    for page in range(1, jumlah_halaman + 1):
        print(f"\n>>> SEDANG MEMPROSES HALAMAN {page} <<<")
        
        # Manipulasi URL: Halaman 1 pakai base_url, halaman berikutnya tambah 'page/X/'
        if page == 1:
            target_url = base_url
        else:
            target_url = f"{base_url}page/{page}/"
            
        html_mentah = fetch_html(target_url)
        
        if html_mentah:
            hasil_per_halaman = parse_events(html_mentah)
            # Gabungkan hasil halaman ini ke list utama
            semua_event.extend(hasil_per_halaman) 

    print("\n======================================")
    print(f"TOTAL EVENT TERKUMPUL: {len(semua_event)} acara")
    print("======================================")
    
    # Cek 3 event terakhir untuk memastikan data halaman 2 masuk
    for event in semua_event[-12:]: 
        print(f"Judul        : {event['nama_event']}")
        print(f"Waktu        : {event['tanggal_waktu']}")
        print(f"Kategori     : {event['kategori']}")
        # print(f"Jenis Event  : {event['jenis_event']}")
        print(f"Source       : {event['source']}")
        print("-" * 100)