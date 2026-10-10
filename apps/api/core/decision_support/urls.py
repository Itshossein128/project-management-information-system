from django.urls import path

from decision_support.views import DecisionCaseViewSet, DecisionRunViewSet

case_list = DecisionCaseViewSet.as_view({'get': 'list', 'post': 'create'})
case_detail = DecisionCaseViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
run_list = DecisionRunViewSet.as_view({'get': 'list', 'post': 'create'})
run_detail = DecisionRunViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    },
)

urlpatterns = [
    path('decision-cases/', case_list, name='project-decision-cases-list'),
    path('decision-cases/<uuid:pk>/', case_detail, name='project-decision-cases-detail'),
    path(
        'decision-cases/<uuid:case_pk>/runs/',
        run_list,
        name='project-decision-runs-list',
    ),
    path(
        'decision-cases/<uuid:case_pk>/runs/<uuid:pk>/',
        run_detail,
        name='project-decision-runs-detail',
    ),
]
