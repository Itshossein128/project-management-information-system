"""Gregorian ↔ Jalali conversion helpers (serializer boundary only)."""
from __future__ import annotations

import datetime

import jdatetime
from django.utils.dateparse import parse_date

JALALI_WEEKDAYS = (
    'شنبه',
    'یک‌شنبه',
    'دوشنبه',
    'سه‌شنبه',
    'چهارشنبه',
    'پنج‌شنبه',
    'جمعه',
)


def gregorian_to_jalali(value: datetime.date) -> str:
    jdate = jdatetime.date.fromgregorian(date=value)
    return jdate.strftime('%Y/%m/%d')


def jalali_to_gregorian(value: str) -> datetime.date:
    normalized = value.strip().replace('-', '/')
    parts = normalized.split('/')
    if len(parts) != 3:
        raise ValueError('Invalid Jalali date format.')
    year, month, day = (int(p) for p in parts)
    return jdatetime.date(year, month, day).togregorian()


def parse_jalali_or_gregorian(value: str) -> datetime.date:
    """Accept Jalali ``1403/07/15`` or ISO Gregorian ``2024-10-06``."""
    text = value.strip()
    if not text:
        raise ValueError('Date is required.')
    if '/' in text:
        return jalali_to_gregorian(text)
    parsed = parse_date(text)
    if parsed is None:
        raise ValueError('Invalid date format.')
    return parsed


def parse_date_optional(value: str | None) -> datetime.date | None:
    """Accept an optional Jalali or ISO Gregorian date."""
    if not value:
        return None
    return parse_jalali_or_gregorian(value)


def persian_day_of_week(value: datetime.date | str) -> str:
    if isinstance(value, str):
        value = parse_jalali_or_gregorian(value)
    jdate = jdatetime.date.fromgregorian(date=value)
    return JALALI_WEEKDAYS[jdate.weekday()]


def to_persian_digits(value: str) -> str:
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    return str(value).translate(str.maketrans(english_digits, persian_digits))


def gregorian_to_jalali_datetime(value: datetime.datetime | None, to_persian: bool = True) -> str:
    if value is None:
        return ''
    from django.utils import timezone

    if timezone.is_aware(value):
        value = timezone.localtime(value)
    jdt = jdatetime.datetime.fromgregorian(datetime=value)
    formatted = jdt.strftime('%Y/%m/%d - %H:%M')
    return to_persian_digits(formatted) if to_persian else formatted
