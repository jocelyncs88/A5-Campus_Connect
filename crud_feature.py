"""CRUD helper untuk data event.

Module ini tidak menyentuh UI dan tidak mengubah layer database.
Fungsinya hanya menyiapkan payload, validasi, dan operasi CRUD berbasis
struktur data database: event_id, nama_event, deskripsi_singkat, gambar_poster,
jenis_event, tanggal_waktu, source, kategori.
"""

from __future__ import annotations

import copy
import re
import uuid
from datetime import datetime

import db_manager


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
    {"field": "tanggal", "label": "Tanggal", "required": True, "db": "tanggal_waktu"},
    {"field": "waktu", "label": "Waktu", "required": True, "db": "tanggal_waktu"},
    {"field": "poster_event", "label": "Poster Event", "required": False, "db": "gambar_poster"},
]

VALID_EVENT_TYPES = {"Internal", "External"}


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _normalize_event_type(value):
    normalized = _clean_text(value).title()
    return normalized if normalized in VALID_EVENT_TYPES else ""


def _normalize_date(value):
    value = _clean_text(value)
    if not value:
        return ""

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _normalize_time(value):
    value = _clean_text(value)
    if not value:
        return ""

    time_range_pattern = r"^([01]?\d|2[0-3]):[0-5]\d\s*-\s*([01]?\d|2[0-3]):[0-5]\d$"
    single_time_pattern = r"^([01]?\d|2[0-3]):[0-5]\d$"

    if re.match(time_range_pattern, value):
        return re.sub(r"\s*[-]\s*", " - ", value)

    if re.match(single_time_pattern, value):
        return value

    return ""


def _row_to_event_dict(row):
    if isinstance(row, dict):
        return {
            "event_id": row.get("event_id", ""),
            "nama_event": row.get("nama_event", "") or "",
            "deskripsi_singkat": row.get("deskripsi_singkat", "") or "",
            "gambar_poster": row.get("gambar_poster", "") or "",
            "jenis_event": row.get("jenis_event", "") or "",
            "tanggal_waktu": row.get("tanggal_waktu", "") or "",
            "source": row.get("source", "") or "",
            "kategori": row.get("kategori", "") or "",
        }

    return {
        "event_id": row[1] if len(row) > 1 else "",
        "nama_event": row[2] if len(row) > 2 and row[2] else "",
        "deskripsi_singkat": row[3] if len(row) > 3 and row[3] else "",
        "gambar_poster": row[4] if len(row) > 4 and row[4] else "",
        "jenis_event": row[5] if len(row) > 5 and row[5] else "",
        "tanggal_waktu": row[6] if len(row) > 6 and row[6] else "",
        "source": row[7] if len(row) > 7 and row[7] else "",
        "kategori": row[8] if len(row) > 8 and row[8] else "",
    }


def _load_existing_events(existing_events=None):
    if existing_events is not None:
        return [_row_to_event_dict(row) for row in existing_events]

    return [_row_to_event_dict(row) for row in db_manager.get_all_events()]


def build_event_payload(form_data):
    """Ubah data form menjadi payload yang sesuai format database."""

    nama_event = _clean_text(form_data.get("nama_event"))
    deskripsi_event = _clean_text(form_data.get("deskripsi_event"))
    jenis_event = _normalize_event_type(form_data.get("jenis_event"))
    kategori_event = _clean_text(form_data.get("kategori_event"))
    tanggal = _normalize_date(form_data.get("tanggal"))
    waktu = _normalize_time(form_data.get("waktu"))
    poster_event = _clean_text(form_data.get("poster_event"))

    tanggal_waktu = f"{tanggal} {waktu}".strip()
    event_id = _clean_text(form_data.get("event_id")) or f"MAN-{uuid.uuid4().hex[:10].upper()}"

    return {
        "event_id": event_id,
        "nama_event": nama_event,
        "deskripsi_singkat": deskripsi_event,
        "gambar_poster": poster_event,
        "jenis_event": jenis_event,
        "tanggal_waktu": tanggal_waktu,
        "source": _clean_text(form_data.get("source")) or "manual",
        "kategori": kategori_event,
        "tanggal": tanggal,
        "waktu": waktu,
    }


def validate_event_payload(payload, existing_events=None, exclude_event_id=None):
    """Validasi payload event sebelum diproses lebih lanjut."""

    errors = {}
    payload = copy.deepcopy(payload)

    if not _clean_text(payload.get("nama_event")):
        errors["nama_event"] = "Nama event wajib diisi."

    if not _clean_text(payload.get("deskripsi_singkat")):
        errors["deskripsi_event"] = "Deskripsi event wajib diisi."

    if payload.get("jenis_event") not in VALID_EVENT_TYPES:
        errors["jenis_event"] = "Jenis event harus Internal atau External."

    if not _clean_text(payload.get("kategori")):
        errors["kategori_event"] = "Kategori event wajib diisi."

    if not _clean_text(payload.get("tanggal")):
        errors["tanggal"] = "Format tanggal harus YYYY-MM-DD."

    if not _clean_text(payload.get("waktu")):
        errors["waktu"] = "Format waktu harus HH:MM atau HH:MM - HH:MM."

    if not _clean_text(payload.get("tanggal_waktu")):
        errors["tanggal_waktu"] = "Gabungan tanggal dan waktu belum valid."

    if not _clean_text(payload.get("source")):
        payload["source"] = "manual"

    existing_records = _load_existing_events(existing_events)
    normalized_name = _clean_text(payload.get("nama_event")).lower()
    normalized_datetime = _clean_text(payload.get("tanggal_waktu")).lower()
    normalized_exclude = _clean_text(exclude_event_id).lower()

    if normalized_name and normalized_datetime:
        for item in existing_records:
            item_event_id = _clean_text(item.get("event_id")).lower()
            if normalized_exclude and item_event_id == normalized_exclude:
                continue
            if (
                _clean_text(item.get("nama_event")).lower() == normalized_name
                and _clean_text(item.get("tanggal_waktu")).lower() == normalized_datetime
            ):
                errors["duplicate"] = "Event dengan nama dan waktu yang sama sudah ada."
                break

    is_valid = len(errors) == 0
    return is_valid, errors, payload


def create_event(form_data, existing_events=None):
    """Buat payload event baru yang siap disimpan ke database."""

    payload = build_event_payload(form_data)
    is_valid, errors, payload = validate_event_payload(payload, existing_events=existing_events)
    return is_valid, errors, payload


def update_event(existing_event, form_data, existing_events=None):
    """Update data event lama lalu kembalikan payload hasil merge."""

    base_event = _row_to_event_dict(existing_event)
    payload = build_event_payload({**base_event, **form_data})
    if not _clean_text(payload.get("event_id")):
        payload["event_id"] = base_event.get("event_id") or f"MAN-{uuid.uuid4().hex[:10].upper()}"

    is_valid, errors, payload = validate_event_payload(
        payload,
        existing_events=existing_events,
        exclude_event_id=base_event.get("event_id"),
    )
    return is_valid, errors, payload


def delete_event(existing_events, event_id):
    """Hapus event dari daftar data di level helper.

    Fungsi ini tidak menulis ke database; ia hanya mengembalikan daftar baru.
    """

    records = _load_existing_events(existing_events)
    target_id = _clean_text(event_id)
    remaining = [item for item in records if _clean_text(item.get("event_id")) != target_id]
    deleted = len(remaining) != len(records)
    return deleted, remaining


def get_event_form_schema():
    return copy.deepcopy(EVENT_FORM_SCHEMA)


def get_db_event_fields():
    return list(DB_EVENT_FIELDS)


def normalize_for_database(form_data, existing_events=None):
    """Shortcut untuk UI: validasi lalu kembalikan payload DB.

    Return:
        (is_valid, errors, payload)
    """

    return create_event(form_data, existing_events=existing_events)
