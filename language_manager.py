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
    "home.filter_free": {"en": "Free", "id": "Gratis"},
    "home.filter_paid": {"en": "Paid", "id": "Berbayar"},

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
    "add_event.field_poster": {"en": "Poster Event", "id": "Poster Event"},
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

    # Kolom header tabel admin
    "admin.col_event_id":   {"en": "Event ID",          "id": "ID Event"},
    "admin.col_event_name": {"en": "Event Name",        "id": "Nama Event"},
    "admin.col_type":       {"en": "Type",              "id": "Jenis"},
    "admin.col_time":       {"en": "Time",              "id": "Waktu"},
    "admin.col_action":     {"en": "Validation Action", "id": "Aksi Validasi"},

    "login.heading": {"en": "Login", "id": "Masuk"},
    "login.have_account": {"en": "Do you already have an account?", "id": "Sudah punya akun?"},
    "login.email_continue": {"en": "Enter your email address to continue", "id": "Masukkan alamat email untuk melanjutkan"},
    "login.forgot_password": {"en": "Forgot password?", "id": "Lupa kata sandi?"},
    "login.continue": {"en": "Continue", "id": "Lanjutkan"},
    "login.no_account": {"en": "Don't have an account yet?", "id": "Belum punya akun?"},
    "login.signup": {"en": "Sign Up", "id": "Daftar"},

    # ── SIGNUP ─────────────────────────────────────────────────
    # Teks kiri (hero)
    "signup.hero_title":            {"en": "Create your\nstudent account",  "id": "Buat akun\nmahasiswa Anda"},
    "signup.big_text":              {"en": "Create your\nstudent account",  "id": "Buat akun\nmahasiswa Anda"},
    "signup.hero_subtitle":         {"en": "Join Campus Connect and discover events, communities, and opportunities around your campus.",
                                     "id": "Bergabung dengan Campus Connect dan temukan event, komunitas, serta peluang di sekitar kampus Anda."},
    "signup.sub_text":              {"en": "Join Campus Connect and discover events, communities, and opportunities around your campus.",
                                     "id": "Bergabung dengan Campus Connect dan temukan event, komunitas, serta peluang di sekitar kampus Anda."},

    # Teks kanan (form header)
    "signup.title":                 {"en": "Sign Up",                       "id": "Daftar"},
    "signup.subtitle":              {"en": "Fill in your information to create your account",
                                     "id": "Isi informasi Anda untuk membuat akun"},

    # Label field
    "signup.label_name":            {"en": "Full Name",                     "id": "Nama Lengkap"},
    "signup.label_email":           {"en": "Email Address",                 "id": "Alamat Email"},
    "signup.label_phone":           {"en": "Phone Number",                  "id": "Nomor Telepon"},
    "signup.label_university":      {"en": "University",                    "id": "Universitas"},
    "signup.label_password":        {"en": "Password",                      "id": "Kata Sandi"},
    "signup.label_confirm":         {"en": "Confirm Password",              "id": "Konfirmasi Kata Sandi"},

    # Placeholder field
    "signup.placeholder_name":      {"en": "Enter your full name",          "id": "Masukkan nama lengkap"},
    "signup.placeholder_email":     {"en": "Enter your email address",      "id": "Masukkan alamat email"},
    "signup.placeholder_phone":     {"en": "Enter your phone number",       "id": "Masukkan nomor telepon"},
    "signup.placeholder_university":{"en": "Enter your university",         "id": "Masukkan universitas"},
    "signup.placeholder_password":  {"en": "Create password",               "id": "Buat kata sandi"},
    "signup.placeholder_confirm":   {"en": "Confirm your password",         "id": "Konfirmasi kata sandi"},

    # Tombol
    "signup.button":                {"en": "Sign Up",                       "id": "Daftar"},
    "signup.back_to_login":         {"en": "← Back to Login",               "id": "← Kembali ke Login"},

    # Popup validasi — nama tidak valid
    "signup.msg_invalid_name_title":    {"en": "Invalid Name",              "id": "Nama Tidak Valid"},
    "signup.msg_invalid_name_body":     {"en": "Full name cannot be empty.", "id": "Nama lengkap tidak boleh kosong."},

    # Popup validasi — data tidak lengkap
    "signup.msg_incomplete_title":      {"en": "Incomplete Data",           "id": "Data Tidak Lengkap"},
    "signup.msg_email_empty":           {"en": "Email must be filled.",     "id": "Email harus diisi."},
    "signup.msg_phone_empty":           {"en": "Phone number must be filled.", "id": "Nomor telepon harus diisi."},
    "signup.msg_password_empty":        {"en": "Password must be filled.",  "id": "Kata sandi harus diisi."},
    "signup.msg_confirm_empty":         {"en": "Confirm password must be filled.", "id": "Konfirmasi kata sandi harus diisi."},
    "signup.msg_university_empty":      {"en": "University must be filled.", "id": "Universitas harus diisi."},

    # Popup validasi — email tidak valid
    "signup.msg_invalid_email_title":   {"en": "Invalid Email",             "id": "Email Tidak Valid"},
    "signup.msg_invalid_email_body":    {"en": "Email must contain '@'.",   "id": "Email harus mengandung '@'."},

    # Popup validasi — nomor telepon tidak valid
    "signup.msg_invalid_phone_title":   {"en": "Invalid Phone Number",      "id": "Nomor Telepon Tidak Valid"},
    "signup.msg_phone_not_digit":       {"en": "Phone number must contain numbers only.", "id": "Nomor telepon hanya boleh berisi angka."},
    "signup.msg_phone_too_long":        {"en": "Phone number maximum is 12 digits.", "id": "Nomor telepon maksimal 12 digit."},

    # Popup validasi — password lemah
    "signup.msg_weak_password_title":   {"en": "Weak Password",             "id": "Kata Sandi Lemah"},
    "signup.msg_weak_password_body":    {"en": "Password must be at least 8 characters.", "id": "Kata sandi minimal 8 karakter."},

    # Popup validasi — password tidak cocok
    "signup.msg_password_mismatch_title": {"en": "Password Error",          "id": "Kesalahan Kata Sandi"},
    "signup.msg_password_mismatch_body":  {"en": "Password and confirm password do not match.", "id": "Kata sandi dan konfirmasi kata sandi tidak cocok."},

    # Popup sukses
    "signup.msg_success_title":         {"en": "Success",                   "id": "Berhasil"},
    "signup.msg_success_body":          {"en": "Account created successfully!", "id": "Akun berhasil dibuat!"},

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
    "upload.upload":          {"en": "Upload",                          "id": "Unggah"},
    "upload.success_uploaded":{"en": "✓ Successfully uploaded",          "id": "✓ Berhasil diunggah"},
    "upload.select_poster":   {"en": "Select Event Poster",              "id": "Pilih Poster Event"},
    "upload.file_too_large":  {"en": "❌ File too large! Max 5MB",        "id": "❌ File terlalu besar! Maksimal 5MB"},
    "upload.use_photo":       {"en": "Use This Photo ✓",                 "id": "Gunakan Foto Ini ✓"},
    "upload.change_photo":    {"en": "Change Photo",                     "id": "Ganti Foto"},
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
}


class LanguageManager(QObject):
    """Singleton — selalu pakai `lang` bukan instansiasi langsung."""

    language_changed = pyqtSignal(str)  # emit kode bahasa baru: "en" atau "id"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super().__new__(cls)
            super(LanguageManager, instance).__init__()  # QObject.__init__
            instance._language = "en"
            instance._initialized = True
            cls._instance = instance
        return cls._instance

    def __init__(self):
        pass

    # ─── PUBLIC API ────────────────────────────────────────────

    @property
    def current(self) -> str:
        """Kode bahasa aktif: 'en' atau 'id'."""
        return self._language

    def set_language(self, code: str) -> None:
        code = code.lower().strip()
        if code not in ("en", "id"):
            raise ValueError(f"Bahasa tidak didukung: {code!r}. Gunakan 'en' atau 'id'.")
        if code != self._language:
            self._language = code
            self.language_changed.emit(code)

    def t(self, key: str, fallback: str = "") -> str:
        entry = _TRANSLATIONS.get(key)
        if entry is None:
            return fallback or key
        return entry.get(self._language, fallback or key)

    def is_english(self) -> bool:
        return self._language == "en"

    def is_indonesian(self) -> bool:
        return self._language == "id"

    @staticmethod
    def raw_event_field(value: str) -> str:
        return value or ""


# ─── SINGLETON GLOBAL ──────────────────────────────────────────
lang = LanguageManager()