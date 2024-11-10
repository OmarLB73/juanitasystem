from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_url'), #(nombre en la url navegador, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('new/', views.proyect_new, name='proyect_new_url'), 

    path('getDataCustomer/', views.getDataCustomer, name='getDataCustomer_url'),
    path('getDataProyectCustomer/', views.getDataProyectCustomer, name='getDataProyectCustomer_url'),

    #path('proyect/view/', views.proyect_view, name='proyect_view_url')
]