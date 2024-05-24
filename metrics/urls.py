from django.urls import path
from .views import get_metric_data, list_metrics, health_data_view, send_report

app_name="metrics"
urlpatterns = [
    path('data/', get_metric_data, name='get_metric_data'),
    path('list/', list_metrics, name='list_metrics'),
    path('submit-health-data/', health_data_view, name='submit_health_data'),
    path('report/', send_report, name='send_report'),
]