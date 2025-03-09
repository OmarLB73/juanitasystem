from django.urls import include, path
from . import views

urlpatterns = [

    #path('user/', include('user.urls')),  # Asegúrate de incluir la app 'user' con su namespace

    path('panel/', views.panel_view, name='panel_url'), #(nombre en la url navegador, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('new/', views.proyect_new, name='proyect_new_url'), 
    path('view/<int:proyect_id>/', views.proyect_view, name='view_url'), 
    path('grafics/', views.grafics_view, name='grafics_url'), 

        
    path('getDataDecorator/', views.getDataDecorator, name='getDataDecorators_url'), 
    path('getDataCustomer/', views.getDataCustomer, name='getDataCustomer_url'),
    path('getDataProyectCustomer/', views.getDataProyectCustomer, name='getDataProyectCustomer_url'),
    path('getAddress/', views.getAddress, name='getAddress_url'),
    path('getDataCalendar/', views.getDataCalendar, name='getDataCalendar_url'),
    path('getDataComment/', views.getDataComment, name='getDataComment_url'),
    path('getDataMaterial/', views.getDataMaterial, name='getDataMaterial_url'),

    path('selectAscociate/', views.selectAscociate, name='getSelectAscociate_url'),
    path('selectSubcategory/', views.selectSubcategory, name='getSelectSubcategory_url'),
    path('selectGroup/', views.selectGroup, name='getSelectGroup_url'),
    path('selectAttibutes/', views.selectAttibutes, name='getSelectAttribute_url'),
    path('selectItems/', views.selectItems, name='getSelectItems_url'),
    path('selectItem/', views.selectItem, name='getSelectItem_url'),
    
    path('saveItem/', views.saveItem, name='saveItem_url'),
    path('saveItemComment/', views.saveItemComment, name='saveItemComment_url'),

    path('deleteItem/', views.deleteItem, name='deleteItem_url'),
    path('deleteProyect/', views.deleteProyect, name='deleteProyect_url'),
    path('deleteItemCommentFile/', views.deleteItemCommentFile, name='deleteItemCommentFile_url'),
    path('deleteComment/', views.deleteComment, name='deleteComment_url'),
    

    path('updateStatus/', views.updateStatus, name='updateStatus_url'),


    

    path('generate_pdf/<int:proyect_id>/', views.generate_pdf, name='generate_pdf'),

    #path('proyect/view/', views.proyect_view, name='proyect_view_url')
]