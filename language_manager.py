# ==============================================================
# FILE: language_manager.py
# TUGAS: Singleton global untuk manajemen bahasa aplikasi
#        Campus Connect (English / Indonesia)
#
# CARA PAKAI:
#   from language_manager import lang
#   label.setText(lang.t("home.title"))
#
# CARA GANTI BAHASA:
#   lang.set_language("en")   # atau "id"
#
# LISTENER perubahan bahasa:
#   lang.language_changed.connect(my_retranslate_fn)
# ==============================================================

from PyQt5.QtCore import QObject, pyqtSignal

# ─────────────────────────────────────────────
# SEMUA STRING UI APLIKASI
# Tambahkan key baru di sini ketika ada halaman baru.
# Konten event (judul, deskripsi, dll.) TIDAK diterjemahkan
# di sini — itu tanggung jawab tiap halaman untuk menampilkan
# versi asli dari database.
# ─────────────────────────────────────────────
_TRANSLATIONS = {
    # ── UMUM / NAVIGASI ────────────────────────────────────────
    "nav.home":             {"en": "  Home",             "id": "  Beranda"},
    "nav.settings":         {"en": "Settings",         "id": "Pengaturan"},
    "nav.notifications":    {"en": "Notifications",    "id": "Notifikasi"},
    "nav.about":            {"en": "  About Us",        "id": "  Tentang Kami"},
    "nav.faq":              {"en": "FAQ",               "id": "FAQ"},
    "nav.logout":           {"en": "Log Out",           "id": "Keluar"},
    "nav.login":            {"en": "  Login",           "id": "  Masuk"},
    "nav.hi_eo":            {"en": "  Hi, Event Organizer!", "id": "  Halo, Event Organizer!"},
    "nav.hi_student":       {"en": "  Hi, Student!",   "id": "  Halo, Mahasiswa!"},
    "nav.admin_panel":      {"en": "  Admin Panel",    "id": "  Panel Admin"},

    # ── TOPBAR SETTINGS ────────────────────────────────────────
    "settings.title":       {"en": "Settings",         "id": "Pengaturan"},
    "settings.home_btn":    {"en": "  Home",            "id": "  Beranda"},

    # ── SIDEBAR SETTINGS ───────────────────────────────────────
    "settings.account":     {"en": "Account",          "id": "Akun"},
    "settings.your_events": {"en": "Your events",      "id": "Event Anda"},
    "settings.notifications":{"en": "Notifications",   "id": "Notifikasi"},
    "settings.appearance":  {"en": "Appearance",       "id": "Tampilan"},
    "settings.language":    {"en": "Language",         "id": "Bahasa"},

    # ── LANGUAGE PANEL ─────────────────────────────────────────
    "lang.panel_title":         {"en": "Language Setting",                  "id": "Pengaturan Bahasa"},
    "lang.panel_subtitle":      {"en": "Select your preferred language for the interface.", "id": "Pilih bahasa yang Anda inginkan untuk tampilan aplikasi"},
    "lang.section_label":       {"en": "App Language",                      "id": "Bahasa Aplikasi"},
    "lang.default_label":       {"en": "Default Language",                  "id": "Bahasa Default"},
    "lang.default_desc":        {"en": "Choose the main language for the Campus Connect interface.",
                                 "id": "Pilih bahasa utama untuk antarmuka Campus Connect."},
    "lang.option_en":           {"en": "English",                           "id": "English"},
    "lang.option_id":           {"en": "Indonesia",                         "id": "Indonesia"},
    "lang.saved_msg":           {"en": "Language preference saved.",        "id": "Preferensi bahasa disimpan."},

    # ── HOMEPAGE ───────────────────────────────────────────────
    "home.search_placeholder":  {"en": "Search events ...",                 "id": "Cari event ..."},
    "home.filter_all":          {"en": "All",                               "id": "Semua"},
    "home.filter_internal":     {"en": "Internal",                          "id": "Internal"},
    "home.filter_external":     {"en": "External",                          "id": "Eksternal"},
    "home.upcoming":            {"en": "Upcoming Events",                   "id": "Event Mendatang"},
    "home.no_events":           {"en": "No events found.",                  "id": "Tidak ada event ditemukan."},
    "home.add_event_btn":       {"en": "+ Add Event",                       "id": "+ Tambah Event"},

    # ── DETAIL EVENT ───────────────────────────────────────────
    "detail.date":              {"en": "Date",                              "id": "Tanggal"},
    "detail.location":          {"en": "Location",                          "id": "Lokasi"},
    "detail.organizer":         {"en": "Organizer",                         "id": "Penyelenggara"},
    "detail.category":          {"en": "Category",                          "id": "Kategori"},
    "detail.ticket":            {"en": "Ticket",                            "id": "Tiket"},
    "detail.free":              {"en": "Free",                              "id": "Gratis"},
    "detail.register_btn":      {"en": "Register Now",                      "id": "Daftar Sekarang"},
    "detail.back_btn":          {"en": "Back",                              "id": "Kembali"},

    # ── ADD / EDIT EVENT ───────────────────────────────────────
    "add_event.title_new":      {"en": "Add New Event",                     "id": "Tambah Event Baru"},
    "add_event.title_edit":     {"en": "Edit Event",                        "id": "Edit Event"},
    "add_event.field_name":     {"en": "Event Name",                        "id": "Nama Event"},
    "add_event.field_desc":     {"en": "Short Description",                 "id": "Deskripsi Singkat"},
    "add_event.field_date":     {"en": "Date",                              "id": "Tanggal"},
    "add_event.field_time":     {"en": "Time",                              "id": "Waktu"},
    "add_event.field_location": {"en": "Location",                          "id": "Lokasi"},
    "add_event.field_category": {"en": "Category",                          "id": "Kategori"},
    "add_event.field_ticket":   {"en": "Ticket Type",                       "id": "Jenis Tiket"},
    "add_event.field_price":    {"en": "Ticket Price",                      "id": "Harga Tiket"},
    "add_event.field_organizer":{"en": "Organizer",                         "id": "Penyelenggara"},
    "add_event.btn_publish":    {"en": "Publish",                           "id": "Publikasikan"},
    "add_event.btn_cancel":     {"en": "Cancel",                            "id": "Batal"},
    "add_event.btn_upload":     {"en": "Upload Poster",                     "id": "Unggah Poster"},

    # ── NOTIFIKASI PANEL ───────────────────────────────────────
    "notif.title":              {"en": "Notifications",                     "id": "Notifikasi"},
    "notif.desc_eo":            {"en": "Manage when you want notifications about registrants for your events.",
                                 "id": "Atur kapan Anda ingin mendapat notifikasi tentang pendaftar event yang Anda buat."},
    "notif.desc_mahasiswa":     {"en": "Manage reminders for events you follow.",
                                 "id": "Atur kapan Anda ingin mendapat pengingat untuk event yang Anda ikuti."},
    "notif.desc_umum":          {"en": "Manage your general notification preferences here.",
                                 "id": "Atur preferensi notifikasi umum Anda di sini."},
    "notif.new_registrant":     {"en": "New registrant",                    "id": "Pendaftar baru"},
    "notif.new_registrant_desc":{"en": "Get alerts every time a user registers",
                                 "id": "Dapatkan peringatan setiap kali pengguna mendaftar"},

    # ── APPEARANCE PANEL ───────────────────────────────────────
    "appearance.title":         {"en": "Appearance",                        "id": "Tampilan"},
    "appearance.coming_soon":   {"en": "Theme and display settings will be available in the next sprint.",
                                 "id": "Pengaturan tema dan tampilan akan hadir di sprint berikutnya."},

    # ── ACCOUNT PANEL ──────────────────────────────────────────
    "account.title":            {"en": "Account",                           "id": "Akun"},
    "account.name":             {"en": "Name",                              "id": "Nama"},
    "account.email":            {"en": "Email",                             "id": "Email"},
    "account.bio":              {"en": "Bio",                               "id": "Bio"},
    "account.contact":          {"en": "Contact",                           "id": "Kontak"},
    "account.save_btn":         {"en": "Save Changes",                      "id": "Simpan Perubahan"},
    "account.change_photo":     {"en": "Change Photo",                      "id": "Ganti Foto"},

    # ── LOGIN ──────────────────────────────────────────────────
    "login.title":              {"en": "Welcome Back!",                     "id": "Selamat Datang Kembali!"},
    "login.email":              {"en": "Email",                             "id": "Email"},
    "login.password":           {"en": "Password",                          "id": "Kata Sandi"},
    "login.btn_login":          {"en": "Log In",                            "id": "Masuk"},
    "login.btn_register":       {"en": "Register",                          "id": "Daftar"},
    "login.or_guest":           {"en": "or continue as Guest",              "id": "atau lanjut sebagai Tamu"},

    # ── ADMIN ──────────────────────────────────────────────────
    "admin.title":              {"en": "Admin Panel",                       "id": "Panel Admin"},
    "admin.approve":            {"en": "Approve",                           "id": "Setujui"},
    "admin.reject":             {"en": "Reject",                            "id": "Tolak"},
    "admin.pending":            {"en": "Pending",                           "id": "Menunggu"},

    # ── YOUR EVENTS ────────────────────────────────────────────
    "your_events.title":        {"en": "Your Events",                       "id": "Event Anda"},
    "your_events.no_events":    {"en": "You have no events yet.",           "id": "Anda belum punya event."},
    "your_events.btn_add":      {"en": "+ Create New Event",                "id": "+ Buat Event Baru"},
    "your_events.btn_edit":     {"en": "Edit",                              "id": "Edit"},
    "your_events.btn_delete":   {"en": "Delete",                            "id": "Hapus"},

    # ── SUCCESS PAGE ───────────────────────────────────────────
    "success.title":            {"en": "Event Submitted!",                  "id": "Event Terkirim!"},
    "success.message":          {"en": "Your event is pending admin review.", "id": "Event Anda menunggu review admin."},
    "success.btn_home":         {"en": "Back to Home",                      "id": "Kembali ke Beranda"},

    # ── ABOUT ──────────────────────────────────────────────────
    "about.title":              {"en": "About Campus Connect",              "id": "Tentang Campus Connect"},

    # ── FAQ ────────────────────────────────────────────────────
    "faq.title":                {"en": "Frequently Asked Questions",        "id": "Pertanyaan yang Sering Diajukan"},

    # ── TOMBOL UMUM ────────────────────────────────────────────
    "btn.ok":                   {"en": "OK",                                "id": "OK"},
    "btn.cancel":               {"en": "Cancel",                            "id": "Batal"},
    "btn.close":                {"en": "Close",                             "id": "Tutup"},
    "btn.save":                 {"en": "Save",                              "id": "Simpan"},
    "btn.back":                 {"en": "Back",                              "id": "Kembali"},
    "btn.confirm":              {"en": "Confirm",                           "id": "Konfirmasi"},

    # ── ERROR / VALIDASI ───────────────────────────────────────
    "err.required":             {"en": "This field is required.",           "id": "Kolom ini wajib diisi."},
    "err.invalid_email":        {"en": "Invalid email format.",             "id": "Format email tidak valid."},
    "err.login_failed":         {"en": "Incorrect email or password.",      "id": "Email atau kata sandi salah."},
    "err.db_error":             {"en": "Database error.",                   "id": "Error database."},
}


class LanguageManager(QObject):
    """Singleton — selalu pakai `lang` bukan instansiasi langsung."""

    language_changed = pyqtSignal(str)  # emit kode bahasa baru: "en" atau "id"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Buat instance baru dan langsung inisialisasi QObject-nya
            instance = super().__new__(cls)
            super(LanguageManager, instance).__init__()  # QObject.__init__
            instance._language = "en"
            instance._initialized = True
            cls._instance = instance
        return cls._instance

    def __init__(self):
        # Semua inisialisasi sudah dilakukan di __new__ — skip di sini
        pass

    # ─── PUBLIC API ────────────────────────────────────────────

    @property
    def current(self) -> str:
        """Kode bahasa aktif: 'en' atau 'id'."""
        return self._language

    def set_language(self, code: str) -> None:
        """
        Ganti bahasa aplikasi.
        code: 'en' atau 'id'
        Mengemit signal language_changed agar semua listener bisa retranslate.
        """
        code = code.lower().strip()
        if code not in ("en", "id"):
            raise ValueError(f"Bahasa tidak didukung: {code!r}. Gunakan 'en' atau 'id'.")
        if code != self._language:
            self._language = code
            self.language_changed.emit(code)

    def t(self, key: str, fallback: str = "") -> str:
        """
        Kembalikan string terjemahan untuk key dan bahasa aktif.
        Jika key tidak ditemukan, kembalikan fallback (atau key itu sendiri).
        """
        entry = _TRANSLATIONS.get(key)
        if entry is None:
            return fallback or key
        return entry.get(self._language, fallback or key)

    def is_english(self) -> bool:
        return self._language == "en"

    def is_indonesian(self) -> bool:
        return self._language == "id"

    # ─── HELPER UNTUK KONTEN EVENT ─────────────────────────────
    # Konten yang dimasukkan EO (judul, deskripsi, lokasi, dll.)
    # TIDAK diterjemahkan — ditampilkan apa adanya dari database.
    # Helper ini hanya untuk kejelasan di kode pemanggil.

    @staticmethod
    def raw_event_field(value: str) -> str:
        """
        Tandai bahwa string ini adalah konten asli event (dari EO).
        Tidak ada terjemahan — dikembalikan apa adanya.
        """
        return value or ""


# ─── SINGLETON GLOBAL ──────────────────────────────────────────
# Import dan pakai langsung:
#   from language_manager import lang
#   label.setText(lang.t("nav.home"))
lang = LanguageManager()