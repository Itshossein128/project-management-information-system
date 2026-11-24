"""Observed daily weather and MET Norway Locationforecast 2.0."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from email.utils import parsedate_to_datetime
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache
from redis.exceptions import RedisError

from field_reports.models import WeatherLog

PROVIDER = 'MET Norway Locationforecast 2.0'
ATTRIBUTION = {
    'provider': PROVIDER,
    'license_url': 'https://creativecommons.org/licenses/by/4.0/',
    'adaptation': 'One forecast sample per project-local day, nearest local noon.',
}
ENDPOINT = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
PROJECT_TIME_ZONE = ZoneInfo('Asia/Tehran')
MIN_CACHE_SECONDS = 3 * 60 * 60
OBSERVED_FIELDS = ('weather_condition', 'temp_min', 'temp_max', 'wind_speed', 'soil_condition')


def _today():
    return datetime.now(PROJECT_TIME_ZONE).date()


def _coordinate(value, maximum):
    number = Decimal(str(value))
    if not number.is_finite() or abs(number) > maximum:
        raise ValueError('Coordinates are out of range.')
    truncated = number.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    return format(truncated.copy_abs() if not truncated else truncated, 'f')


def _forecast_payload(coordinates, *, cache_only=False):
    key = f'b01:metno:v1:{coordinates["lat"]}:{coordinates["lon"]}'
    previous = cache.get(key)
    now = datetime.now(timezone.utc)
    if previous and previous['refresh_after'] > now:
        return previous['timeseries']
    if cache_only:
        return None
    if not cache.add(f'{key}:request', True, timeout=5):
        return None
    if cache.get(f'{key}:backoff'):
        return None

    headers = {
        'User-Agent': settings.MET_NORWAY_USER_AGENT,
        'Accept': 'application/json',
    }
    if previous and previous['last_modified']:
        headers['If-Modified-Since'] = previous['last_modified']
    request = Request(f'{ENDPOINT}?{urlencode(coordinates)}', headers=headers)
    try:
        try:
            with urlopen(request, timeout=3) as response:
                timeseries = json.load(response)['properties']['timeseries']
                if not isinstance(timeseries, list) or not timeseries:
                    raise ValueError('Missing forecast timeseries.')
                last_modified = response.headers.get('Last-Modified')
                expires = response.headers.get('Expires')
        except HTTPError as error:
            with error:
                if error.code != 304 or previous is None:
                    raise
                timeseries = previous['timeseries']
                last_modified = error.headers.get('Last-Modified') or previous['last_modified']
                expires = error.headers.get('Expires')
    except (OSError, ValueError, TypeError, KeyError):
        cache.set(f'{key}:backoff', True, timeout=60)
        return None

    refresh_after = now + timedelta(seconds=MIN_CACHE_SECONDS)
    if expires:
        try:
            refresh_after = max(refresh_after, parsedate_to_datetime(expires))
        except (TypeError, ValueError):
            pass
    cache.set(key, {
        'refresh_after': refresh_after, 'last_modified': last_modified, 'timeseries': timeseries,
    }, timeout=max(int((refresh_after - now).total_seconds()), 0) + 24 * 60 * 60)
    return timeseries


def _daily_samples(timeseries, dates):
    samples = {}
    for hour in timeseries:
        local = datetime.fromisoformat(hour['time'].replace('Z', '+00:00')).astimezone(PROJECT_TIME_ZONE)
        if local.date() not in dates:
            continue
        observation = hour['data']
        temp = observation['instant']['details'].get('air_temperature')
        if not isinstance(temp, (int, float)):
            continue
        symbol = None
        for period in ('next_1_hours', 'next_6_hours', 'next_12_hours'):
            symbol = observation.get(period, {}).get('summary', {}).get('symbol_code')
            if symbol:
                break
        distance = abs(local.hour * 60 + local.minute - 12 * 60)
        if local.date() not in samples or distance < samples[local.date()][0]:
            samples[local.date()] = (distance, {
                'date': local.date().isoformat(), 'forecast_time': local.isoformat(),
                'air_temperature_c': temp, 'symbol_code': symbol,
            })
    if all(day in samples for day in dates):
        return [samples[day][1] for day in dates]
    return []


def get_three_day_forecast(latitude, longitude, *, report_date, cache_only=False):
    result = {
        'provider': PROVIDER, 'coordinates': None, 'days': [], 'status': 'unknown',
        'unavailable_reason': None, 'attribution': ATTRIBUTION.copy(),
    }
    if latitude is None or longitude is None:
        return {**result, 'unavailable_reason': 'missing_coordinates'}
    try:
        result['coordinates'] = {'lat': _coordinate(latitude, 90), 'lon': _coordinate(longitude, 180)}
    except (InvalidOperation, ValueError):
        return {**result, 'unavailable_reason': 'invalid_coordinates'}
    today = _today()
    if not today <= report_date <= today + timedelta(days=6):
        return {**result, 'unavailable_reason': 'outside_forecast_window'}

    dates = [report_date + timedelta(days=offset) for offset in (1, 2, 3)]
    try:
        timeseries = (
            _forecast_payload(result['coordinates'], cache_only=True)
            if cache_only else _forecast_payload(result['coordinates'])
        )
        if timeseries is None:
            return {**result, 'unavailable_reason': 'provider_unavailable'}
        days = _daily_samples(timeseries, dates)
    except (RedisError, KeyError, TypeError, ValueError):
        return {**result, 'unavailable_reason': 'provider_unavailable'}
    if not days:
        return {**result, 'unavailable_reason': 'incomplete_forecast'}
    return {**result, 'status': 'ok', 'days': days}


def get_observed_weather_summary(project, report_date):
    log = WeatherLog.objects.filter(project=project, log_date=report_date).values(*OBSERVED_FIELDS).first()
    readings = {field: (log or {}).get(field) for field in OBSERVED_FIELDS}
    readings = {field: None if value == '' else value for field, value in readings.items()}
    return {
        **readings, 'source': 'weather_logs',
        'log_date': report_date.isoformat() if log is not None else None,
        'status': 'ok' if all(value is not None for value in readings.values()) else 'unknown',
    }


def capture_report_weather(report, *, cache_only=False):
    report_date = date.fromisoformat(report.report_date) if isinstance(report.report_date, str) else report.report_date
    observed = get_observed_weather_summary(report.project, report_date)
    forecast = get_three_day_forecast(
        report.project.latitude, report.project.longitude, report_date=report_date, cache_only=cache_only,
    )
    return {
        'observed_source': observed['source'],
        'observed_status': observed['status'],
        'log_date': observed['log_date'],
        **{field: observed[field] for field in OBSERVED_FIELDS},
        'forecast_provider': forecast['provider'],
        'forecast_status': forecast['status'],
        'forecast_days': forecast['days'],
        'forecast_unavailable_reason': forecast['unavailable_reason'],
        'forecast_attribution': forecast['attribution'],
    }


def report_weather_evidence(report, *, preview=False):
    if report.status != 'approved' and report.is_current:
        return capture_report_weather(report, cache_only=not preview)
    return report.export_weather_snapshot or {
        'observed_source': 'weather_logs', 'observed_status': 'unknown', 'log_date': None,
        **dict.fromkeys(OBSERVED_FIELDS),
        'forecast_provider': PROVIDER, 'forecast_status': 'unknown', 'forecast_days': [],
        'forecast_unavailable_reason': 'no_version_evidence', 'forecast_attribution': ATTRIBUTION.copy(),
    }
