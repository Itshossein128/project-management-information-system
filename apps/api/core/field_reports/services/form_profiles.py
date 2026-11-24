"""Select reference-form positions independently of the project's labor catalog."""
from collections.abc import Mapping
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from field_reports.services.data_contract import load_daily_report_contract

SHIRAZ_PROFILE = 'shiraz-34-32-v1'


@dataclass(frozen=True)
class FormPresentationProfile:
    code: str
    indirect_slots: tuple[str, ...]
    direct_slots: tuple[str, ...]
    appendix_heading_en: str
    appendix_heading_fa: str


def load_form_presentation_profile(profile_code=SHIRAZ_PROFILE):
    profiles = load_daily_report_contract()['form_profiles']
    if profile_code not in profiles:
        raise ValidationError(_('Unknown daily report form profile.'))
    profile = profiles[profile_code]
    return FormPresentationProfile(
        code=profile_code,
        indirect_slots=tuple(profile['indirect_slots']),
        direct_slots=tuple(profile['direct_slots']),
        appendix_heading_en=profile['appendix_heading_en'],
        appendix_heading_fa=profile['appendix_heading_fa'],
    )


def resolve_labor_rows_for_profile(labor_rows, profile_code=SHIRAZ_PROFILE):
    profile = load_form_presentation_profile(profile_code)
    standard = {
        'indirect': {title: [] for title in profile.indirect_slots},
        'direct': {title: [] for title in profile.direct_slots},
    }
    appendix = {'indirect': [], 'direct': []}
    for row in labor_rows:
        if isinstance(row, Mapping):
            category = row.get('labor_category', row.get('category'))
            job_title, custom_title = row['job_title'], row.get('custom_title')
        else:
            category, job_title, custom_title = row.labor_category, row.job_title, row.custom_title
        if category not in standard:
            raise ValidationError(_('Unknown labor category.'))
        if custom_title in (None, '', job_title) and job_title in standard[category]:
            standard[category][job_title].append(row)
        else:
            appendix[category].append(row)

    return {
        'profile_code': profile.code,
        'standard_indirect': [{'title': title, 'rows': rows} for title, rows in standard['indirect'].items()],
        'standard_direct': [{'title': title, 'rows': rows} for title, rows in standard['direct'].items()],
        'appendix_indirect': appendix['indirect'],
        'appendix_direct': appendix['direct'],
        'appendix_heading_en': profile.appendix_heading_en,
        'appendix_heading_fa': profile.appendix_heading_fa,
    }
