from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('login/', views.login_view, name='login'), #(nombre en la url, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('dashboard/', views.dashboard_view, name='dashboard'), #(nombre en la url, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('proyect/', views.proyect_view, name='proyect'), #(nombre en la url, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    
    #path('logout/', views.logout_view, name='logout'),
    #path('register/', views.register_view, name='register'),    
    path('validate-username/', views.validate_username, name='validate_username'),

]