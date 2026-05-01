"""Validation helpers for event payloads (package copy).

Contains pure functions that validate payloads produced by
`crud_events.crud_feature.build_event_payload`. Does not perform DB writes;
accepts optional `existing_events` list for duplicate checks.
"""

from __future__ import annotations

import copy
import re
from datetime import datetime


VALID_EVENT_TYPES = {"Internal", "External"}


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _is_valid_date(value: str) -> bool:
    if not value:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_valid_time(value: str) -> bool:
    if not value:
        return False
    time_range_pattern = r"^([01]?\d|2[0-3]):[0-5]\d\s*-\s*([01]?\d|2[0-3]):[0-5]\d$"
    single_time_pattern = r"^([01]?\d|2[0-3]):[0-5]\d$"
    return bool(re.match(time_range_pattern, value) or re.match(single_time_pattern, value))


def _normalize_datetime_str(date_str: str, time_str: str) -> str:
    date_str = _clean_text(date_str)
    time_str = _clean_text(time_str)
    if not date_str and not time_str:
        return ""
    return f"{date_str} {time_str}".strip()


def validate_payload(payload: dict, existing_events: list | None = None, exclude_event_id: str | None = None):
    """Validate an event payload.

    Returns (is_valid: bool, errors: dict)
    """
    errors = {}
    p = copy.deepcopy(payload)

    if not _clean_text(p.get("nama_event")):
        errors["nama_event"] = "Nama event wajib diisi."

    if not _clean_text(p.get("deskripsi_singkat")):
        errors["deskripsi_event"] = "Deskripsi event wajib diisi."

    if p.get("jenis_event") not in VALID_EVENT_TYPES:
        errors["jenis_event"] = "Jenis event harus Internal atau External."

    if not _clean_text(p.get("kategori")):
        errors["kategori_event"] = "Kategori event wajib diisi."

    # date/time validation
    date_ok = _is_valid_date(p.get("tanggal", ""))
    time_ok = _is_valid_time(p.get("waktu", ""))
    if not date_ok:
        errors["tanggal"] = "Format tanggal harus YYYY-MM-DD."
    if not time_ok:
        errors["waktu"] = "Format waktu harus HH:MM atau HH:MM - HH:MM."

    # combined key for duplicate check
    combined = _normalize_datetime_str(p.get("tanggal", ""), p.get("waktu", ""))
    if not combined:
        errors["tanggal_waktu"] = "Gabungan tanggal dan waktu belum valid."

    # duplicate check (simple in-memory check)
    if existing_events:
        name = _clean_text(p.get("nama_event")).lower()
        for r in existing_events:
            rid = _clean_text(r.get("event_id") if isinstance(r, dict) else "")
            if exclude_event_id and rid == (exclude_event_id or ""):
                continue
            r_name = _clean_text(r.get("nama_event") if isinstance(r, dict) else "").lower()
            r_datetime = _clean_text(r.get("tanggal_waktu") if isinstance(r, dict) else "").lower()
            if r_name == name and r_datetime == combined.lower():
                errors["duplicate"] = "Event dengan nama dan waktu yang sama sudah ada."
                break

    return len(errors) == 0, errors
