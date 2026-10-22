import pytest
from rest_framework import status

from field_reports.models import WeatherCondition, WeatherLog, SiteStatus


@pytest.fixture
def weather_url(project):
    return f'/api/v1/projects/{project.id}/weather/'


@pytest.mark.django_db
class TestWeatherLogList:
    def test_unauthenticated_cannot_list(self, api_client, weather_url):
        response = api_client.get(weather_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_empty(self, auth_client, weather_url):
        response = auth_client.get(weather_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    def test_viewer_can_list(self, api_client, other_user, viewer_member, weather_url, project, user):
        WeatherLog.objects.create(
            project=project,
            log_date='2024-06-01',
            weather_condition=WeatherCondition.CLEAR,
            site_status=SiteStatus.ACTIVE,
            created_by=user,
        )
        api_client.force_authenticate(user=other_user)
        response = api_client.get(weather_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestWeatherLogCreate:
    def test_create_with_jalali_date(self, auth_client, weather_url):
        response = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/12',
                'temp_max': '35.5',
                'temp_min': '22.0',
                'weather_condition': 'clear',
                'site_status': 'active',
                'wind_speed': '15 km/h NW',
                'soil_condition': 'Dry / Moderate',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['log_date'] == '1403/03/12'
        assert response.data['day_of_week'] == 'شنبه'
        assert response.data['weather_condition_label'] == 'آفتابی / صاف'
        assert response.data['wind_speed'] == '15 km/h NW'
        assert response.data['soil_condition'] == 'Dry / Moderate'

    def test_duplicate_date_returns_409(self, auth_client, weather_url, project, user):
        WeatherLog.objects.create(
            project=project,
            log_date='2024-06-01',
            weather_condition=WeatherCondition.CLEAR,
            site_status=SiteStatus.ACTIVE,
            created_by=user,
        )
        response = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/12',
                'weather_condition': 'cloudy',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data['error']['message'] == 'گزارش جوی برای این تاریخ قبلاً ثبت شده است'

    def test_viewer_cannot_create(self, api_client, other_user, weather_url):
        api_client.force_authenticate(user=other_user)
        response = api_client.post(
            weather_url,
            {
                'log_date': '1403/03/12',
                'weather_condition': 'clear',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_temperature_boundaries_accepted(self, auth_client, weather_url):
        response = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/13',
                'temp_min': '-40.0',
                'temp_max': '60.0',
                'weather_condition': 'snowy',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_temperature_out_of_bounds_rejected(self, auth_client, weather_url):
        res_low = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/14',
                'temp_min': '-40.5',
                'weather_condition': 'snowy',
                'site_status': 'active',
            },
            format='json',
        )
        assert res_low.status_code == status.HTTP_400_BAD_REQUEST

        res_high = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/15',
                'temp_max': '60.5',
                'weather_condition': 'clear',
                'site_status': 'active',
            },
            format='json',
        )
        assert res_high.status_code == status.HTTP_400_BAD_REQUEST

    def test_temp_max_less_than_temp_min_rejected(self, auth_client, weather_url):
        response = auth_client.post(
            weather_url,
            {
                'log_date': '1403/03/16',
                'temp_min': '25.0',
                'temp_max': '15.0',
                'weather_condition': 'clear',
                'site_status': 'active',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        err = response.data.get('error', {})
        code = response.data.get('code') or err.get('code')
        details = response.data.get('details') or err.get('details', {})
        assert code == 'temp_max_must_be_gte_temp_min'
        assert 'temp_max' in details

    def test_legacy_weather_rejected(self, auth_client, weather_url):
        for retired in ('sunny', 'partly_cloudy', 'foggy'):
            res = auth_client.post(
                weather_url,
                {
                    'log_date': '1403/03/17',
                    'weather_condition': retired,
                    'site_status': 'active',
                },
                format='json',
            )
            assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestWeatherLogUpdate:
    def test_partial_patch_temp_max_below_stored_temp_min_rejected(self, auth_client, weather_url, project, user):
        log = WeatherLog.objects.create(
            project=project,
            log_date='2024-06-20',
            temp_min='20.0',
            temp_max='30.0',
            weather_condition=WeatherCondition.CLEAR,
            site_status=SiteStatus.ACTIVE,
            created_by=user,
        )
        detail_url = f'{weather_url}{log.id}/'
        res = auth_client.patch(detail_url, {'temp_max': '10.0'}, format='json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        err = res.data.get('error', {})
        code = res.data.get('code') or err.get('code')
        details = res.data.get('details') or err.get('details', {})
        assert code == 'temp_max_must_be_gte_temp_min' or 'temp_max' in details


@pytest.mark.django_db
class TestWeatherLogSoftDelete:
    def test_soft_delete_excludes_from_list(self, auth_client, weather_url, project, user):
        entry = WeatherLog.objects.create(
            project=project,
            log_date='2024-06-01',
            weather_condition=WeatherCondition.RAINY,
            site_status=SiteStatus.INACTIVE,
            created_by=user,
        )
        detail_url = f'{weather_url}{entry.id}/'
        response = auth_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        entry.refresh_from_db()
        assert entry.is_deleted is True
        assert entry.deleted_at is not None

        list_response = auth_client.get(weather_url)
        assert list_response.data['results'] == []


@pytest.mark.django_db
class TestWeatherLogFilters:
    def test_date_range_filter(self, auth_client, weather_url, project, user):
        WeatherLog.objects.create(
            project=project,
            log_date='2024-06-01',
            weather_condition=WeatherCondition.CLEAR,
            site_status=SiteStatus.ACTIVE,
            created_by=user,
        )
        WeatherLog.objects.create(
            project=project,
            log_date='2024-06-15',
            weather_condition=WeatherCondition.CLOUDY,
            site_status=SiteStatus.ACTIVE,
            created_by=user,
        )
        response = auth_client.get(f'{weather_url}?date_from=1403/03/01&date_to=1403/03/15')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
