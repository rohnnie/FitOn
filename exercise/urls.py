from django.urls import path
from exercise import views

app_name="exercise"
urlpatterns = [
    path('list/', views.list_exercises, name='list_exercises'),
    path('store/', views.store_exercises, name='store_exercises'),
]