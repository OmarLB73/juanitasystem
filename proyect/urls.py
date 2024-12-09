from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.panel_view, name='panel_url'), #(nombre en la url navegador, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('new/', views.proyect_new, name='proyect_new_url'), 
    path('view/<int:proyect_id>/', views.proyect_view, name='view_url'), 
    path('grafics/', views.grafics_view, name='grafics_url'), 

    
    
    path('getDataDecorator/', views.getDataDecorator, name='getDataDecorators_url'),
    path('selectAscociate/', views.selectAscociate, name='getSelectAscociate_url'),
    path('getAddress/', views.getAddress, name='getAddress_url'),




    path('getDataCustomer/', views.getDataCustomer, name='getDataCustomer_url'),
    path('getDataProyectCustomer/', views.getDataProyectCustomer, name='getDataProyectCustomer_url'),

    #path('proyect/view/', views.proyect_view, name='proyect_view_url')
]