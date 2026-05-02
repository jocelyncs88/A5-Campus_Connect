"""Schema definitions for Add Event form and DB mapping (package copy).

This is used inside the `crud_events` package.
"""

from copy import deepcopy


DB_EVENT_FIELDS = [
    "event_id",
    "nama_event",
    "deskripsi_singkat",
    "gambar_poster",
    "jenis_event",
    "tanggal_waktu",
    "source",
    "kategori",
]


EVENT_FORM_SCHEMA = [
    {"field": "nama_event", "label": "Nama Event", "required": True, "db": "nama_event"},
    {"field": "deskripsi_event", "label": "Deskripsi Event", "required": True, "db": "deskripsi_singkat"},
    {"field": "jenis_event", "label": "Jenis Event", "required": True, "db": "jenis_event"},
    {"field": "kategori_event", "label": "Kategori Event", "required": True, "db": "kategori"},
    {"field": "tanggal", "label": "Tanggal (YYYY-MM-DD)", "required": True, "db": "tanggal_waktu"},
    {"field": "waktu", "label": "Waktu (HH:MM or HH:MM - HH:MM)", "required": True, "db": "tanggal_waktu"},
    {"field": "poster_event", "label": "Poster Event (path/url)", "required": False, "db": "gambar_poster"},
]


def get_db_event_fields():
    return list(DB_EVENT_FIELDS)


def get_event_form_schema():
    return deepcopy(EVENT_FORM_SCHEMA)
