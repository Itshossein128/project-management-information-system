from django.urls import path

from field_reports.views import WeatherLogViewSet

weather_list = WeatherLogViewSet.as_view({'get': 'list', 'post': 'create'})
weather_detail = WeatherLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

urlpatterns = [
    path('weather/', weather_list, name='project-weather-list'),
    path('weather/<uuid:pk>/', weather_detail, name='project-weather-detail'),
]
