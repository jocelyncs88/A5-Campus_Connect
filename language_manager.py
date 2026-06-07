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


    # ── TAMBAHAN UI MULTILINGUAL ───────────────────────────────
    "home.welcome_to": {"en": "Welcome to,", "id": "Selamat datang di,"},
    "home.filter_type": {"en": "Type:", "id": "Tipe:"},
    "home.filter_ticket": {"en": "Ticket:", "id": "Tiket:"},
    "home.filter_source": {"en": "Source:", "id": "Sumber:"},
    "home.filter_free":     {"en": "Free",            "id": "Gratis"},
    "home.filter_paid":     {"en": "Paid",            "id": "Berbayar"},
    "home.filter_official": {"en": "Official Polban", "id": "Resmi Polban"},
    "home.filter_partner":  {"en": "Partnership",     "id": "Kemitraan"},

    "about.hero_title": {"en": "About Us", "id": "Tentang Kami"},
    "about.subtitle": {"en": "Helping students discover campus events, communities, and opportunities in one place.", "id": "Membantu mahasiswa menemukan event kampus, komunitas, dan peluang dalam satu tempat."},
    "about.built_title": {"en": "Built for Campus Life", "id": "Dibuat untuk Kehidupan Kampus"},
    "about.built_body": {"en": "Campus Connect is a desktop application designed to help students find campus events faster, easier, and more centrally. It connects academic life with social activities, so students can stay informed and involved.", "id": "Campus Connect adalah aplikasi desktop yang dirancang untuk membantu mahasiswa menemukan event kampus dengan lebih cepat, mudah, dan terpusat. Aplikasi ini menghubungkan kehidupan akademik dengan aktivitas sosial agar mahasiswa tetap mendapatkan informasi dan terlibat aktif."},
    "about.mission_title": {"en": "Our Mission", "id": "Misi Kami"},
    "about.mission_body": {"en": "We aim to make campus information more accessible and encourage students to grow beyond the classroom through events, communities, and collaboration.", "id": "Kami bertujuan membuat informasi kampus lebih mudah diakses dan mendorong mahasiswa berkembang di luar kelas melalui event, komunitas, dan kolaborasi."},
    "about.discover_title": {"en": "Discover", "id": "Temukan"},
    "about.discover_body": {"en": "Find campus events quickly.", "id": "Temukan event kampus dengan cepat."},
    "about.connect_title": {"en": "Connect", "id": "Terhubung"},
    "about.connect_body": {"en": "Bridge students and organizers.", "id": "Jembatani mahasiswa dan penyelenggara."},
    "about.participate_title": {"en": "Participate", "id": "Berpartisipasi"},
    "about.participate_body": {"en": "Explore opportunities beyond class.", "id": "Jelajahi peluang di luar kelas."},
    "about.team_title": {"en": "Development Team", "id": "Tim Pengembang"},
    "about.team_name": {"en": "INFORMATICS A5 TEAM", "id": "TIM INFORMATIKA A5"},
    "about.team_member": {"en": "A5 Team Member", "id": "Anggota Tim A5"},
    "about.footer": {"en": "© 2026 Campus Connect · Academic Serenity for the Modern Student", "id": "© 2026 Campus Connect · Academic Serenity for the Modern Student"},

    "add_event.subtitle_new": {"en": "Fill in the event details completely so participants can find it easily", "id": "Lengkapi detail event agar peserta dapat menemukannya dengan mudah"},
    "add_event.subtitle_edit": {"en": "Update the details of the published event", "id": "Perbarui detail event yang sudah dipublikasi"},
    "add_event.section_main": {"en": "MAIN INFORMATION", "id": "INFORMASI UTAMA"},
    "add_event.field_name_req": {"en": "Event Name *", "id": "Nama Event *"},
    "add_event.field_type_req": {"en": "Event Type *", "id": "Tipe Event *"},
    "add_event.field_desc_req": {"en": "Event Description *", "id": "Deskripsi Event *"},
    "add_event.field_category_req": {"en": "Event Category *", "id": "Kategori Event *"},
    "add_event.section_time_venue": {"en": "Time & Venue", "id": "Waktu & Tempat"},
    "add_event.field_date_req": {"en": "Date *", "id": "Tanggal *"},
    "add_event.field_time_req": {"en": "Time *", "id": "Waktu *"},
    "add_event.field_location_req": {"en": "Location *", "id": "Lokasi *"},
    "add_event.field_campus_req": {"en": "Campus Name *", "id": "Nama Kampus *"},
    "add_event.field_ticket_req": {"en": "Ticket Type *", "id": "Jenis Tiket *"},
    "add_event.field_price_req": {"en": "Ticket Price (Rp) *", "id": "Harga Tiket (Rp) *"},
    "add_event.field_poster": {"en": "Poster Event *", "id": "Poster Event *"},
    "add_event.ph_name": {"en": "Enter event name", "id": "Masukkan nama event"},
    "add_event.ph_desc": {"en": "Enter event description", "id": "Masukkan deskripsi event"},
    "add_event.ph_category": {"en": "Seminar/Competition/Workshop/Recruitment/etc", "id": "Seminar/Kompetisi/Workshop/Rekrutmen/dll"},
    "add_event.ph_location": {"en": "Enter event location", "id": "Masukkan lokasi event"},
    "add_event.ph_campus": {"en": "Enter campus name", "id": "Masukkan nama kampus"},
    "add_event.ph_price": {"en": "Enter ticket price using numbers only, e.g. 1000", "id": "Masukkan harga tiket dengan angka saja, contoh 1000"},
    "add_event.select_type": {"en": "Select event type", "id": "Pilih tipe event"},
    "add_event.upload_hint": {"en": "Click to\nupload poster", "id": "Klik untuk\nunggah poster"},
    "add_event.free": {"en": "Free", "id": "Gratis"},
    "add_event.paid": {"en": "Paid", "id": "Berbayar"},
    "add_event.btn_publish_full": {"en": "✓  Publish Event!", "id": "✓  Publikasikan Event!"},
    "add_event.btn_save_changes": {"en": "✓  Save Changes", "id": "✓  Simpan Perubahan"},
    "add_event.validation_failed": {"en": "Validation Failed", "id": "Validasi Gagal"},
    "add_event.err_required_check": {"en": "Please check all required fields and try again.", "id": "Mohon periksa semua kolom wajib dan coba lagi."},
    "add_event.err_select_type": {"en": "Please select the Event Type!", "id": "Mohon pilih tipe event!"},
    "add_event.err_upload_poster": {"en": "Please upload the event poster!", "id": "Mohon unggah poster event!"},
    "add_event.err_date_empty": {"en": "Date has not been entered!", "id": "Tanggal belum diisi!"},
    "add_event.err_time_empty": {"en": "Time has not been entered!", "id": "Waktu belum diisi!"},
    "add_event.err_date_past": {"en": "Event date cannot be in the past!", "id": "Tanggal event tidak boleh di masa lalu!"},
    "add_event.err_time_past": {"en": "For today's event, the time cannot be earlier than the current time!", "id": "Untuk event hari ini, waktu tidak boleh lebih awal dari waktu sekarang!"},
    "add_event.err_price_empty": {"en": "Please enter the ticket price!", "id": "Mohon masukkan harga tiket!"},
    "add_event.err_price_min": {"en": "Ticket price must be at least 4 digits (minimum Rp1000)!", "id": "Harga tiket minimal 4 digit (minimal Rp1000)!"},

    "detail.no_image": {"en": "No Image", "id": "Tidak Ada Gambar"},
    "detail.book": {"en": "Book", "id": "Pesan"},
    "detail.booked": {"en": "Booked", "id": "Sudah Dipesan"},
    "detail.external": {"en": "External", "id": "Eksternal"},
    "detail.internal": {"en": "Internal", "id": "Internal"},
    "detail.overview": {"en": "Overview", "id": "Ringkasan"},
    "detail.location_empty": {"en": "Location is not available", "id": "Lokasi belum tersedia"},
    "detail.date_empty": {"en": "Date is not available", "id": "Tanggal belum tersedia"},
    "detail.organizer_empty": {"en": "Organizer is not available", "id": "Penyelenggara belum tersedia"},
    "detail.desc_empty": {"en": "Description is not available", "id": "Deskripsi belum tersedia"},
    "detail.login_required_title": {"en": "Login Required", "id": "Login Diperlukan"},
    "detail.login_required_book": {"en": "You must login as a student first to book this event.", "id": "Anda harus login sebagai mahasiswa terlebih dahulu untuk memesan event ini."},
    "detail.login_required_like": {"en": "You must login as a student first to like this event.", "id": "Anda harus login sebagai mahasiswa terlebih dahulu untuk menyukai event ini."},
    "detail.access_denied_title": {"en": "Access Denied", "id": "Akses Ditolak"},
    "detail.access_denied_book": {"en": "Only student accounts can book events.", "id": "Hanya akun mahasiswa yang dapat memesan event."},
    "detail.access_denied_like": {"en": "Only student accounts can like events.", "id": "Hanya akun mahasiswa yang dapat menyukai event."},

    "admin.validation_dashboard": {"en": "Event Validation Dashboard", "id": "Dashboard Validasi Event"},
    "admin.validation_subtitle": {"en": "Manage event validation queue from Event Organizers", "id": "Kelola antrean validasi event dari Event Organizer"},
    "admin.return_home": {"en": "← Return to Homepage", "id": "← Kembali ke Beranda"},
    "admin.btn_approve_full": {"en": "✓ Approve", "id": "✓ Setujui"},
    "admin.btn_decline_full": {"en": "✗ Decline", "id": "✗ Tolak"},

    "login.heading": {"en": "Login", "id": "Masuk"},
    "login.have_account": {"en": "Do you already have an account?", "id": "Sudah punya akun?"},
    "login.email_continue": {"en": "Enter your email address to continue", "id": "Masukkan alamat email untuk melanjutkan"},
    "login.forgot_password": {"en": "Forgot password?", "id": "Lupa kata sandi?"},
    "login.continue": {"en": "Continue", "id": "Lanjutkan"},
    "login.no_account": {"en": "Don't have an account yet?", "id": "Belum punya akun?"},
    "login.signup": {"en": "Sign Up", "id": "Daftar"},
    "login.email_placeholder":  {"en": "Enter email address",              "id": "Masukkan alamat email"},
    "login.return_home":       {"en": "← Back to Homepage",               "id": "← Kembali ke Beranda"},
    "login.contact_us":        {"en": "Contact us",                        "id": "Hubungi Kami"},
    "login.admin_help":        {"en": "Contact the admin to register as an Event Organizer or sign up as a student",                              
                                "id": "Hubungi admin untuk mendaftar sebagai Event Organizer atau daftar sebagai mahasiswa"},

    # "account.name_desc":               {"en": "Your name can only be changed once every 30 days.",                                      "id": "Nama hanya dapat diubah setiap 30 hari sekali."},
    "account.bio_desc":                {"en": "You can edit your bio anytime.",                                                          "id": "Anda dapat mengubah bio kapan saja."},
    "account.email_desc_organizer":    {"en": "Enter a professional email address for event inquiries and booking requests.",             "id": "Masukkan email profesional untuk pertanyaan dan pemesanan event."},
    "account.email_desc_user":         {"en": "Enter your email address to receive notifications, e-tickets, and event updates.",         "id": "Masukkan email untuk menerima notifikasi, e-ticket, dan update event."},
    "account.contact_desc_organizer":  {"en": "Add a phone number so audiences can contact you about events or collaborations.",          "id": "Tambahkan nomor telepon agar peserta dapat menghubungi Anda terkait event atau kolaborasi."},
    "account.contact_desc_user":       {"en": "Add your phone number so organizers can contact you about event updates.",                 "id": "Tambahkan nomor telepon agar penyelenggara dapat menghubungi Anda terkait update event."},

    "notif.push_translated":           {"en": "Push",                                                                                    "id": "Dorong"},
    "msg.login_success_role":          {"en": "Successful Login as {role}!",                                                             "id": "Berhasil masuk sebagai {role}!"},

    "signup.hero_title": {"en": "Create your\nstudent account", "id": "Buat akun\nmahasiswa Anda"},
    "signup.hero_subtitle": {"en": "Join Campus Connect and discover events, communities, and opportunities around your campus.", "id": "Bergabung dengan Campus Connect dan temukan event, komunitas, serta peluang di sekitar kampus Anda."},
    "signup.title": {"en": "Sign Up", "id": "Daftar"},
    "signup.subtitle": {"en": "Fill in your information to create your account", "id": "Isi informasi Anda untuk membuat akun"},
    "signup.full_name": {"en": "Full Name", "id": "Nama Lengkap"},
    "signup.email": {"en": "Email Address", "id": "Alamat Email"},
    "signup.phone": {"en": "Phone Number", "id": "Nomor Telepon"},
    "signup.university": {"en": "University", "id": "Universitas"},
    "signup.password": {"en": "Password", "id": "Kata Sandi"},
    "signup.confirm_password": {"en": "Confirm Password", "id": "Konfirmasi Kata Sandi"},
    "signup.ph_name": {"en": "Enter your full name", "id": "Masukkan nama lengkap"},
    "signup.ph_email": {"en": "Enter your email address", "id": "Masukkan alamat email"},
    "signup.ph_phone": {"en": "Enter your phone number", "id": "Masukkan nomor telepon"},
    "signup.ph_university": {"en": "Enter your university", "id": "Masukkan universitas"},
    "signup.ph_password": {"en": "Create password", "id": "Buat kata sandi"},
    "signup.ph_confirm": {"en": "Confirm your password", "id": "Konfirmasi kata sandi"},
    "signup.button": {"en": "Sign Up", "id": "Daftar"},
    "signup.back_login": {"en": "← Back to Login", "id": "← Kembali ke Login"},

    "faq.subtitle": {"en": "Campus Connect Help Center", "id": "Pusat Bantuan Campus Connect"},
    "faq.footer": {"en": "© 2026 Campus Connect Team", "id": "© 2026 Tim Campus Connect"},
    "faq.q1": {"en": "What is Campus Connect?", "id": "Apa itu Campus Connect?"},
    "faq.a1": {"en": "Campus Connect is an application that helps students find and manage campus events more easily.", "id": "Campus Connect adalah aplikasi yang membantu mahasiswa menemukan dan mengelola event kampus dengan lebih mudah."},
    "faq.q2": {"en": "Do I need to log in first?", "id": "Apakah saya harus login terlebih dahulu?"},
    "faq.a2": {"en": "Some features require login first to keep your account secure.", "id": "Beberapa fitur tertentu memerlukan login terlebih dahulu untuk menjaga keamanan akun."},
    "faq.q3": {"en": "Can I see upcoming events?", "id": "Apakah bisa melihat event yang akan datang?"},
    "faq.a3": {"en": "Yes, all upcoming events can be viewed directly from the homepage.", "id": "Ya, seluruh event yang akan datang dapat dilihat langsung pada halaman utama aplikasi."},
    "faq.q4": {"en": "How do I add an event?", "id": "Bagaimana cara menambahkan event?"},
    "faq.a4": {"en": "Users can add events through the Add Event menu in the top-right area of the application.", "id": "Pengguna dapat menambahkan event melalui menu Add Event pada bagian kanan atas aplikasi."},
    "faq.q5": {"en": "Who developed this application?", "id": "Siapa pengembang aplikasi ini?"},
    "faq.a5": {"en": "This application was developed by the A5 Informatics POLBAN team as a software development project.", "id": "Aplikasi ini dikembangkan oleh kelompok A5 Informatika POLBAN sebagai proyek pengembangan perangkat lunak."},

    "notif.mark_all_read": {"en": "Mark all as read", "id": "Tandai semua dibaca"},
    "notif.tap_to_view": {"en": "Tap to view →", "id": "Ketuk untuk melihat →"},
    "notif.event_status": {"en": "Event Status", "id": "Status Event"},
    "notif.event_approval_status": {"en": "Event approval status", "id": "Status persetujuan event"},
    "notif.event_approval_desc": {"en": "Always receive updates when the admin approves or rejects your submitted event.", "id": "Selalu terima update ketika admin menyetujui atau menolak event yang Anda kirim."},
    "notif.always_on": {"en": "Always on", "id": "Selalu aktif"},
    "notif.push": {"en": "Push", "id": "Push"},
    "notif.registration_tickets": {"en": "Registration & Tickets", "id": "Pendaftaran & Tiket"},
    "notif.new_registrant_desc_full": {"en": "Get alerts every time a user registers or purchases a ticket.", "id": "Dapatkan peringatan setiap kali pengguna mendaftar atau membeli tiket."},
    "notif.cancellations": {"en": "Registration cancellations", "id": "Pembatalan pendaftaran"},
    "notif.cancellations_desc": {"en": "Notification if a participant cancels their booking.", "id": "Notifikasi jika peserta membatalkan pemesanan."},
    "notif.quota_alerts": {"en": "Critical updates", "id": "Update penting"},
    "notif.quota_alerts_desc": {"en": "Automatic warnings when your event capacity reaches 90% and when sold out.", "id": "Peringatan otomatis saat kapasitas event mencapai 90% dan saat habis."},
    "notif.my_schedule": {"en": "My Schedule", "id": "Jadwal Saya"},
    "notif.event_reminder": {"en": "Event reminder", "id": "Pengingat event"},
    "notif.event_reminder_desc": {"en": "Stay on track with alerts 1 day before your event start.", "id": "Dapatkan pengingat 1 hari sebelum event dimulai."},
    "notif.discovery": {"en": "Discovery", "id": "Penemuan"},
    "notif.interest_match": {"en": "Interest match", "id": "Sesuai minat"},
    "notif.interest_match_desc": {"en": "Get notified about new events that match your favorite.", "id": "Dapatkan notifikasi event baru yang sesuai dengan favorit Anda."},
    "notif.campus_spotlight": {"en": "Campus Spotlight", "id": "Sorotan Kampus"},
    "notif.campus_spotlight_desc": {"en": "Exclusive updates on internal events from your university's organizations.", "id": "Update khusus event internal dari organisasi universitas Anda."},

    "account.settings_title": {"en": "Account Settings", "id": "Pengaturan Akun"},
    "account.change_photo_lower": {"en": "Change photo", "id": "Ganti foto"},
    "account.bio_placeholder": {"en": "My account is all about....", "id": "Akun saya tentang...."},
    "account.char_limit_reached": {"en": "Character limit reached", "id": "Batas karakter tercapai"},
    "account.char_limit_exceeded": {"en": "Character limit exceeded", "id": "Batas karakter terlampaui"},
    "account.invalid_input": {"en": "Invalid Input", "id": "Input Tidak Valid"},
    "account.login_required_title": {"en": "Login Required", "id": "Login Diperlukan"},
    "account.login_required_msg": {"en": "You need to log in first to edit Account Settings.", "id": "Anda harus login terlebih dahulu untuk mengedit Pengaturan Akun."},
    "account.add_name": {"en": "Add your preferred name", "id": "Tambahkan nama pilihan Anda"},
    "account.add_email": {"en": "Add an email", "id": "Tambahkan email"},
    "account.add_phone": {"en": "Add phone", "id": "Tambahkan telepon"},
    "account.phone_placeholder": {"en": "Enter phone number", "id": "Masukkan nomor telepon"},
    "account.email_placeholder": {"en": "Enter your email", "id": "Masukkan email Anda"},
    "account.crop_hint": {"en": "Drag the box to choose the photo area  •  Scroll to zoom", "id": "Geser kotak untuk memilih area foto  •  Scroll untuk zoom"},
    "account.zoom": {"en": "Zoom", "id": "Zoom"},
    "account.preview": {"en": "Preview", "id": "Pratinjau"},
    "account.crop_ratio": {"en": "Crop ratio", "id": "Rasio crop"},

    "account.invalid_image": {"en": "Invalid image file.", "id": "File gambar tidak valid."},
    "account.crop_open_failed": {"en": "Failed to open crop dialog:", "id": "Gagal membuka crop dialog:"},

    "account.free_crop": {"en": "Free", "id": "Bebas"},

    "your_events.settings_title": {"en": "Your Events Settings", "id": "Pengaturan Event Anda"},
    "your_events.published": {"en": "Published Events", "id": "Event Terpublikasi"},
    "your_events.empty_created": {"en": "You haven't created any events yet!", "id": "Anda belum membuat event apa pun!"},
    "your_events.create_first": {"en": "<u>Create your first event now!</u>", "id": "<u>Buat event pertama Anda sekarang!</u>"},
    "your_events.my_events": {"en": "My Events", "id": "Event Saya"},
    "your_events.booked_events": {"en": "Booked Events", "id": "Event Dipesan"},
    "your_events.liked_events": {"en": "Liked Events", "id": "Event Disukai"},
    "your_events.empty_booked": {"en": "You haven't booked any events yet.", "id": "Anda belum memesan event apa pun."},
    "your_events.empty_liked": {"en": "You haven't liked any events yet.", "id": "Anda belum menyukai event apa pun."},
    "your_events.get_ticket": {"en": "Get ticket", "id": "Ambil tiket"},
    "your_events.payment": {"en": "Payment", "id": "Pembayaran"},
    "your_events.payment_soon": {"en": "Payment feature will be available soon!", "id": "Fitur pembayaran akan tersedia segera!"},
    "your_events.booking_failed": {"en": "Booking Failed", "id": "Pemesanan Gagal"},
    "your_events.event_id_missing": {"en": "Event ID is missing.", "id": "Event ID tidak ditemukan."},
    "your_events.failed_book": {"en": "Failed to book event:", "id": "Gagal memesan event:"},


    "msg.success": {"en": "Success", "id": "Berhasil"},
    "msg.failed": {"en": "Failed", "id": "Gagal"},
    "msg.logout": {"en": "Logout", "id": "Keluar"},
    "msg.logout_confirm": {"en": "Are you sure you want to logout?", "id": "Apakah Anda yakin ingin keluar?"},
    "msg.logout_success": {"en": "Successfully logout.", "id": "Berhasil keluar."},
    "msg.login_success": {"en": "Login Successful!", "id": "Login Berhasil!"},
    "msg.login_failed": {"en": "Email or Password is incorrect!", "id": "Email atau kata sandi salah!"},
    "msg.booking_success": {"en": "Booking Success", "id": "Pemesanan Berhasil"},
    "msg.failed_publish": {"en": "Failed to Publish Event", "id": "Gagal Mempublikasikan Event"},
    "msg.registration_failed": {"en": "Registration Failed", "id": "Pendaftaran Gagal"},


    "success.submitted_success": {"en": "Event submitted successfully!", "id": "Event berhasil dikirim!"},
    "success.view_event": {"en": "View Event", "id": "Lihat Event"},
    "success.create_another": {"en": "Create Another Event", "id": "Buat Event Lain"},
    "upload.title": {"en": "Upload Poster Event", "id": "Unggah Poster Event"},
    "upload.click": {"en": "Click to upload poster", "id": "Klik untuk mengunggah poster"},
    "upload.format": {"en": "PNG, JPG max 5MB", "id": "PNG, JPG maksimal 5MB"},
    "upload.ratio": {"en": "Portrait ratio recommended", "id": "Rasio portrait disarankan"},
    "upload.uploading": {"en": "Uploading...", "id": "Sedang mengunggah..."},
    "upload.dont_close": {"en": "Don't close this window", "id": "Jangan tutup jendela ini"},
    "upload.upload": {"en": "Upload", "id": "Unggah"},
    "msg.error": {"en": "Error", "id": "Error"},
    "msg.invalid_update_request": {"en": "Invalid update request format.", "id": "Format request update tidak valid."},
    "msg.update_request_not_found": {"en": "Update request not found.", "id": "Request update tidak ditemukan."},
    "msg.process_update_failed": {"en": "Failed to process update request.", "id": "Gagal memproses request update."},

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

    # ── ADMIN TABLE COLUMNS ────────────────────────────────────
    "admin.col_event_id":       {"en": "Event ID",                         "id": "ID Event"},
    "admin.col_event_name":     {"en": "Event Name",                       "id": "Nama Event"},
    "admin.col_type":           {"en": "Type",                             "id": "Tipe"},
    "admin.col_time":           {"en": "Time",                             "id": "Waktu"},
    "admin.col_action":         {"en": "Validation Action",                "id": "Aksi Validasi"},

    # ── NOTIFICATION MESSAGES ──────────────────────────────────
    "notif.msg_new_event_title":{"en": "🏫 New campus event: {event}",     "id": "🏫 Event kampus baru: {event}"},
    "notif.msg_new_event_body": {"en": "\"{event}\" from your campus is now live on Campus Connect! Be the first to know and grab your spot.",
                                 "id": "\"{event}\" dari kampus Anda sekarang tersedia di Campus Connect! Jadilah yang pertama tahu dan ambil tempatmu."},

    # ── ACCOUNT PLACEHOLDERS & FILE DIALOG ────────────────────
    "account.add_name_ph":          {"en": "add name",                                          "id": "tambah nama"},
    "account.add_bio_ph":           {"en": "add bio",                                           "id": "tambah bio"},
    "account.add_email_ph":         {"en": "add email",                                         "id": "tambah email"},
    "account.add_contact_ph":       {"en": "add contact",                                       "id": "tambah kontak"},
    "account.select_profile_photo": {"en": "Select Profile Photo",                              "id": "Pilih Foto Profil"},
    "account.image_filter":         {"en": "Images (*.png *.jpg *.jpeg *.webp *.bmp)",          "id": "Gambar (*.png *.jpg *.jpeg *.webp *.bmp)"},

    # ── ACCOUNT PHONE VALIDATION ERRORS ───────────────────────
    "account.err_phone_empty":      {"en": "Phone number cannot be empty.",                     "id": "Nomor telepon tidak boleh kosong."},
    "account.err_phone_digits_only":{"en": "Phone number can only contain numbers.",            "id": "Nomor telepon hanya boleh berisi angka."},
    "account.err_phone_start_8":    {"en": "Phone number must start with 8 after +62.",         "id": "Nomor telepon harus diawali dengan 8 setelah +62."},
    "account.err_phone_length":     {"en": "Phone number must be 9–13 digits after +62.",       "id": "Nomor telepon harus 9–13 digit setelah +62."},

    # ── UPLOAD POSTER DIALOG — key yang hilang ─────────────────
    "upload.use_photo":       {"en": "Use This Photo",           "id": "Gunakan Foto Ini"},
    "upload.change_photo":    {"en": "Change Photo",             "id": "Ganti Foto"},
    "upload.success_uploaded":{"en": "✓ Successfully uploaded",  "id": "✓ Berhasil diunggah"},
    "upload.select_poster":   {"en": "Select Poster Image",      "id": "Pilih Gambar Poster"},
    "upload.file_too_large":  {"en": "File is too large! Max 5MB.", "id": "File terlalu besar! Maks 5MB."},

    # ── NOTIFICATION SETTINGS — key yang hilang ────────────────
    "notif.critical_updates":      {"en": "Critical updates",    "id": "Update penting"},
    "notif.critical_updates_desc": {"en": "Get notified when details of an event you booked are changed by the organizer.",
                                    "id": "Dapatkan notifikasi saat detail event yang Anda daftarkan diubah oleh penyelenggara."},

    # ── NOTIFICATION EMPTY STATE ───────────────────────────────
    "notif.empty_login":   {"en": "Please log in to view your notifications.",
                            "id": "Silakan masuk untuk melihat notifikasi Anda."},
    "notif.empty_no_notif":{"en": "You're all caught up! No notifications yet.",
                            "id": "Semuanya sudah terbaca! Belum ada notifikasi."},

    # ── NOTIFICATION RELATIVE TIME ─────────────────────────────
    "notif.time_just_now":   {"en": "Just now",          "id": "Baru saja"},
    "notif.time_minutes_ago":{"en": "{n} minute{s} ago", "id": "{n} menit yang lalu"},
    "notif.time_hours_ago":  {"en": "{n} hour{s} ago",   "id": "{n} jam yang lalu"},
    "notif.time_yesterday":  {"en": "Yesterday",          "id": "Kemarin"},
    "notif.time_days_ago":   {"en": "{n} days ago",       "id": "{n} hari yang lalu"},

    # ── NOTIFICATION MESSAGES (disimpan ke DB saat notif dibuat) ─
    "notif.msg_new_registrant_title": {"en": "New Registrant for {event}!",
                                       "id": "Pendaftar Baru untuk {event}!"},
    "notif.msg_new_registrant_body":  {"en": "Congrats! There's a new registrant for \"{event}\". Your event now has {total} registrant{suffix}. Keep up the momentum!",
                                       "id": "Selamat! Ada pendaftar baru untuk \"{event}\". Event Anda sekarang memiliki {total} pendaftar. Pertahankan momentumnya!"},
    "notif.msg_cancellation_title":   {"en": "📋 Cancellation: {event}",
                                       "id": "📋 Pembatalan: {event}"},
    "notif.msg_cancellation_body":    {"en": "A participant has cancelled their registration for \"{event}\". Your event now has {sisa} registrant{suffix} remaining.",
                                       "id": "Seorang peserta telah membatalkan pendaftarannya untuk \"{event}\". Event Anda sekarang memiliki {sisa} pendaftar tersisa."},
    "notif.msg_approved_title":       {"en": "Event Approved ✅",    "id": "Event Disetujui ✅"},
    "notif.msg_approved_body":        {"en": "\"{event}\" has been approved by the admin and is now live on Campus Connect! Your event is ready to accept registration.",
                                       "id": "\"{event}\" telah disetujui oleh admin dan sekarang tayang di Campus Connect! Event Anda siap menerima pendaftaran."},
    "notif.msg_rejected_title":       {"en": "Event Rejected ❌",    "id": "Event Ditolak ❌"},
    "notif.msg_rejected_body":        {"en": "\"{event}\" has been rejected by the admin. Please double-check the event details or contact the admin for further information.",
                                       "id": "\"{event}\" ditolak oleh admin. Silakan periksa kembali detail event atau hubungi admin untuk informasi lebih lanjut."},
    "notif.msg_update_approved_title":{"en": "Event Update Approved ✅",  "id": "Pembaruan Event Disetujui ✅"},
    "notif.msg_update_approved_body": {"en": "Changes for \"{event}\" have been approved by the admin and the event has been updated.",
                                       "id": "Perubahan untuk \"{event}\" telah disetujui oleh admin dan event sudah diperbarui."},
    "notif.msg_update_rejected_title":{"en": "Event Update Rejected ❌",  "id": "Pembaruan Event Ditolak ❌"},
    "notif.msg_update_rejected_body": {"en": "Changes for \"{event}\" were rejected by the admin. The original event remains unchanged.",
                                       "id": "Perubahan untuk \"{event}\" ditolak oleh admin. Event asli tetap tidak berubah."},
    "notif.msg_h1_title":             {"en": "🔔 Reminder: {event} is tomorrow!",
                                       "id": "🔔 Pengingat: {event} adalah besok!"},
    "notif.msg_h1_body":              {"en": "Don't forget — \"{event}\" is happening tomorrow at {time}. Get ready!",
                                       "id": "Jangan lupa — \"{event}\" akan berlangsung besok pukul {time}. Bersiaplah!"},
    "notif.msg_event_updated_title":  {"en": "📢 Event Update: {event}",
                                       "id": "📢 Pembaruan Event: {event}"},
    "notif.msg_event_updated_body":   {"en": "\"{event}\" has been updated by the organizer. Please check the latest event details to stay up to date.",
                                       "id": "\"{event}\" telah diperbarui oleh penyelenggara. Silakan cek detail event terbaru agar tetap terinformasi."},
    "notif.msg_interest_title":       {"en": "✨ New event you might like!",
                                       "id": "✨ Event baru yang mungkin Anda suka!"},
    "notif.msg_interest_body":        {"en": "\"{event}\" is a new {kategori} event that matches your interests based on your liked events. Check it out!",
                                       "id": "\"{event}\" adalah event {kategori} baru yang sesuai minat Anda berdasarkan event yang pernah Anda sukai. Cek sekarang!"},
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