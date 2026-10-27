"""Bilingual lifecycle error messages for daily reports."""
from __future__ import annotations

from typing import Optional
from django.utils.translation import get_language
from rest_framework.exceptions import ErrorDetail

LIFECYCLE_MESSAGES = {
    'report_not_in_submittable_state': {
        'fa': 'فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند',
        'en': 'Only draft or rejected reports can be submitted.',
    },
    'rejection_reason_required': {
        'fa': 'دلیل رد الزامی است',
        'en': 'Rejection reason is required.',
    },
    'rejection_reason_min_length_10': {
        'fa': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد',
        'en': 'Rejection reason must be at least 10 characters.',
    },
    'quantity_unset_invalid': {
        'fa': 'مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود',
        'en': 'Work quantity must be specified; enter zero if no work was performed.',
    },
    'correction_already_open': {
        'fa': 'درخواست اصلاح باز برای این گزارش وجود دارد',
        'en': 'An open correction request already exists for this report.',
    },
    'reason_required': {
        'fa': 'دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد',
        'en': 'Correction reason must be at least 10 characters.',
    },
    'report_not_locked': {
        'fa': 'فقط گزارش قفل‌شده جاری قابل اصلاح است',
        'en': 'Only current approved reports can be corrected.',
    },
    'correction_not_open': {
        'fa': 'فقط درخواست اصلاح باز قابل لغو است',
        'en': 'Only open correction requests can be cancelled.',
    },
    'result_not_cancellable': {
        'fa': 'گزارش نتیجه دیگر پیش‌نویس نیست و قابل لغو نیست',
        'en': 'Result report is not a draft and cannot be cancelled.',
    },
    'source_not_restorable': {
        'fa': 'نسخه مبنای اصلاح قابل بازگردانی نیست',
        'en': 'Base report cannot be restored.',
    },
}


def get_lifecycle_msg(code: str, request=None) -> str:
    """Return localized lifecycle message.

    Defaults to Persian for standard calls or 'fa' headers;
    returns English when requested via Accept-Language: en or translation.override('en').
    """
    lang = 'fa'
    if request is not None and hasattr(request, 'META'):
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept:
            primary = accept.split(',')[0].strip().lower()
            if primary.startswith('en'):
                lang = 'en'
            elif primary.startswith('fa'):
                lang = 'fa'
    else:
        from django.utils.translation.trans_real import _active
        active_trans = getattr(_active, 'value', None)
        if active_trans and hasattr(active_trans, 'to_language'):
            active_lang = active_trans.to_language()
            if active_lang.startswith('en'):
                lang = 'en'
            elif active_lang.startswith('fa'):
                lang = 'fa'
        else:
            cur = (get_language() or '').lower()
            if cur.startswith('fa'):
                lang = 'fa'

    entry = LIFECYCLE_MESSAGES.get(code, {})
    return entry.get(lang) or entry.get('fa') or ''


def lifecycle_error_detail(code: str, request=None) -> ErrorDetail:
    """Helper returning an ErrorDetail with stable code and localized message."""
    return ErrorDetail(get_lifecycle_msg(code, request=request), code=code)
