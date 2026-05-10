"""CRU(D) helpers inside `crud_events` package.

Build payloads and orchestrate validation; keep DB writes via `db_manager`.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Tuple

from .event_schema import get_event_form_schema, get_db_event_fields
from .validation_crud import validate_payload
import db_manager


_INDONESIAN_MONTHS = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]


def _format_date_for_storage(date_value: str) -> str:
    text = (date_value or "").strip()
    if not text:
        return ""

    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return text

    month_name = _INDONESIAN_MONTHS[parsed.month - 1]
    return f"{parsed.day:02d} {month_name} {parsed.year}"


def build_event_payload(form_data: dict) -> dict:
    nama_event = (form_data.get("nama_event") or "").strip()
    deskripsi = (form_data.get("deskripsi_event") or "").strip()
    jenis = (form_data.get("jenis_event") or "").strip().title()
    kategori = (form_data.get("kategori_event") or "").strip()
    tanggal = (form_data.get("tanggal") or "").strip()
    waktu = (form_data.get("waktu") or "").strip()
    poster = (form_data.get("poster_event") or "").strip()
    tanggal_storage = _format_date_for_storage(tanggal)

    tanggal_waktu = f"{tanggal_storage} {waktu}".strip()
    event_id = (form_data.get("event_id") or "").strip() or f"MAN-{uuid.uuid4().hex[:10].upper()}"

    return {
        "event_id": event_id,
        "nama_event": nama_event,
        "deskripsi_singkat": deskripsi,
        "gambar_poster": poster,
        "jenis_event": jenis,
        "tanggal_waktu": tanggal_waktu,
        "source": (form_data.get("source") or "manual").strip(),
        "kategori": kategori,
        "tanggal": tanggal,
        "waktu": waktu,
    }


def prepare_create(form_data: dict, existing_events: list | None = None) -> Tuple[bool, dict, dict]:
    payload = build_event_payload(form_data)
    ok, errors = validate_payload(payload, existing_events=existing_events)
    return ok, errors, payload


def prepare_update(existing_event_row, form_data: dict, existing_events: list | None = None) -> Tuple[bool, dict, dict]:
    base = {}
    if isinstance(existing_event_row, dict):
        base = existing_event_row
    else:
        base = {
            "event_id": existing_event_row[1] if len(existing_event_row) > 1 else "",
            "nama_event": existing_event_row[2] if len(existing_event_row) > 2 else "",
            "deskripsi_singkat": existing_event_row[3] if len(existing_event_row) > 3 else "",
            "gambar_poster": existing_event_row[4] if len(existing_event_row) > 4 else "",
            "jenis_event": existing_event_row[5] if len(existing_event_row) > 5 else "",
            "tanggal_waktu": existing_event_row[6] if len(existing_event_row) > 6 else "",
            "source": existing_event_row[7] if len(existing_event_row) > 7 else "",
            "kategori": existing_event_row[8] if len(existing_event_row) > 8 else "",
        }

    merged = {**base, **form_data}
    payload = build_event_payload(merged)
    ok, errors = validate_payload(payload, existing_events=existing_events, exclude_event_id=base.get("event_id"))
    return ok, errors, payload


def save_payload(payload: dict) -> None:
    db_manager.upsert_event(payload)


def get_form_schema():
    return get_event_form_schema()


def get_db_fields():
    return get_db_event_fields()
