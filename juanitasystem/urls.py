"""
URL configuration for juanitasystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

#Add URL maps to redirect the base URL to our application
from django.views.generic import RedirectView

from django.urls import path, include

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('user/', include('user.urls')),  # Esto incluye las vistas de la app user
    path('proyect/', include('proyect.urls')),  # Esto incluye las vistas de la app proyect

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', RedirectView.as_view(url='user/login/', permanent=True)),

]
