from django.urls import path
from . import views
from metrics.views import get_metric_data

app_name="user"
urlpatterns = [
    path('callback/', views.callback_google_fit, name='callback_google_fit'),
    path('authorize/', views.authorize_google_fit, name='authorize_google_fit'),
    path('home/', get_metric_data, name='home_dashboard'),
    path('account/', views.account_page, name='account'),
    path("registration/", views.register, name="user_registration"),
    path("login/", views.loginView, name="login"),
    path("passwordReset/", views.passwordResetView, name="passwordReset"),
    path("logout/", views.logoutView, name="logout"),
    path(
        "passwordResetConfirm/<uidb64>/<token>",
        views.passwordResetConfirmView,
        name="passwordResetConfirm",
    ),
]