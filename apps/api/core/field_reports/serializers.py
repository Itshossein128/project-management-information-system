from rest_framework import serializers

from common.jalali import persian_day_of_week
from common.serializers import JalaliDateField
from field_reports.models import SiteStatus, WeatherCondition, WeatherLog


class WeatherLogSerializer(serializers.ModelSerializer):
    log_date = JalaliDateField()
    day_of_week = serializers.CharField(read_only=True)
    weather_condition_label = serializers.CharField(
        source='get_weather_condition_display',
        read_only=True,
    )
    site_status_label = serializers.CharField(
        source='get_site_status_display',
        read_only=True,
    )

    class Meta:
        model = WeatherLog
        fields = [
            'id',
            'log_date',
            'day_of_week',
            'temp_max',
            'temp_min',
            'weather_condition',
            'weather_condition_label',
            'site_status',
            'site_status_label',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'day_of_week', 'created_at', 'updated_at']

    def validate(self, attrs):
        temp_min = attrs.get('temp_min', getattr(self.instance, 'temp_min', None))
        temp_max = attrs.get('temp_max', getattr(self.instance, 'temp_max', None))
        if temp_min is not None and temp_max is not None and temp_min > temp_max:
            raise serializers.ValidationError(
                {'temp_min': 'حداقل دما نمی‌تواند بیشتر از حداکثر دما باشد.'},
            )
        log_date = attrs.get('log_date', getattr(self.instance, 'log_date', None))
        if log_date:
            attrs['day_of_week'] = persian_day_of_week(log_date)
        return attrs


class WeatherLogCreateSerializer(WeatherLogSerializer):
    class Meta(WeatherLogSerializer.Meta):
        pass
