from config.exceptions import ConflictError
from field_reports.models import WeatherLog

def check_weather_log_conflict(project_id, log_date):
    if WeatherLog.objects.filter(project_id=project_id, log_date=log_date).exists():
        raise ConflictError('گزارش جوی برای این تاریخ قبلاً ثبت شده است')
