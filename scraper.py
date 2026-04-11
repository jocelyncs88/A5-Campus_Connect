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
        nama_event = title_tag.text.strip() if title_tag else "Judul Tidak Diketahui"

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
            "tanggal_waktu": "TBA",
            "source": "Scraped_WebPolban"
        }

        scraped_data_list.append(event_data)

    return scraped_data_list

# ==========================================
# ENTRY POINT (TESTING)
# ==========================================
# Blok ini HARUS di paling bawah agar bisa memanggil fungsi-fungsi di atasnya
if __name__ == "__main__":
    target_url = "https://www.polban.ac.id/category/kemahasiswaan/event/"
    
    # Alur 1: Ambil data mentah
    html_mentah = fetch_html(target_url)
    
    if html_mentah:
        # Alur 2: Bedah datanya
        hasil_scraping = parse_events(html_mentah)
        
        # Alur 3: Tampilkan hasilnya
        print("\n--- HASIL EKSTRAKSI DATA ---")
        for event in hasil_scraping: 
            print(f"ID     : {event['event_id']}")
            print(f"Judul  : {event['nama_event']}")
            print(f"Gambar : {event['gambar_poster']}")
            print(f"Desc   : {event['deskripsi_singkat']}")
            print("-" * 40)