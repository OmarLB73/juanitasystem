from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'  # Asegúrate de tener esto en la parte superior

urlpatterns = [
    path('login/', views.custom_login, name='login_url'),     
    path('logout/', views.logout_view, name='logout_url'),
]