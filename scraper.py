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
        raw_title = title_tag.text.strip() if title_tag else "Judul Tidak Diketahui"

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

        # Bungkus ke dalam Dictionary
        event_data = {
            "event_id": event_id,
            "nama_event": nama_event,
            "deskripsi_singkat": deskripsi_singkat,
            "gambar_poster": gambar_poster,
            "jenis_event": "External",
            "tanggal_waktu": tanggal_waktu,
            "source": "Scraped_WebPolban"
        }

        scraped_data_list.append(event_data)

    return scraped_data_list

# ==========================================
# ENTRY POINT (TESTING)
# ==========================================
if __name__ == "__main__":
    base_url = "https://www.polban.ac.id/category/kemahasiswaan/event/"
    
    # KONSEP LECTURER: Penggunaan List utama untuk menampung gabungan data dari semua halaman
    semua_event = []
    
    # Targetkan 2 halaman saja dulu untuk MVP
    jumlah_halaman = 4 

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
    for event in semua_event[-4:]: 
        print(f"Judul  : {event['nama_event']}")
        print(f"Waktu  : {event['tanggal_waktu']}")
        print("-" * 40)