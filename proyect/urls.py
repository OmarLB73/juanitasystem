from django.urls import include, path
# from . import views
from .views.proyects_views import panel_view, proyect_new, proyect_view, grafics_view, pdf_view
from .views.ajax_select_views import getDataDecorator, getDataCustomer, getAddress, getDataCalendar, getDataModal, getDataMaterial, getDataItem, getDataWO, getStateValidate, selectAscociate, selectSubcategory, selectGroup, selectAttibutes, selectWOs, addWorkOrder
from .views.ajax_save_views import saveSessionState, saveItem, saveComment, saveCalendar, saveQuote, saveMaterial, saveWO, updateStatus
from .views.ajax_delete_views import deleteItem, deleteProyect, deleteItemCommentFile, deleteComment, deleteCommentCalendar, deleteFile, deleteTaskCalendar

urlpatterns = [

    #path('user/', include('user.urls')),  # Asegúrate de incluir la app 'user' con su namespace

    path('panel/', panel_view, name='panel_url'), #(nombre en la url navegador, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('new/', proyect_new, name='proyect_new_url'), 
    path('view/<int:proyect_id>/', proyect_view, name='view_url'), 
    path('calendar/', panel_view, name='calendar_url'), #(nombre en la url navegador, nombre de la vista en el archivo views.py, nombre de la variable que se usa en la vista)
    path('grafics/', grafics_view, name='grafics_url'), 
    path('generate_pdf/<int:workorderId>/', pdf_view, name='generate_pdf'),

        
    path('getDataDecorator/', getDataDecorator, name='getDataDecorators_url'), 
    path('getDataCustomer/', getDataCustomer, name='getDataCustomer_url'),
    # path('getDataProyectCustomer/', views.getDataProyectCustomer, name='getDataProyectCustomer_url'),
    path('getAddress/', getAddress, name='getAddress_url'),
    path('getDataCalendar/', getDataCalendar, name='getDataCalendar_url'),
    path('getDataModal/', getDataModal, name='getDataModal_url'),
    path('getDataMaterial/', getDataMaterial, name='getDataMaterial_url'),
    path('getDataItem/', getDataItem, name='getDataItem_url'),
    path('getDataWO/', getDataWO, name='getDataWO_url'),
    path('getStateValidate/', getStateValidate, name='getStateValidate_url'),

    path('selectAscociate/', selectAscociate, name='getSelectAscociate_url'),
    path('selectSubcategory/', selectSubcategory, name='getSelectSubcategory_url'),
    path('selectGroup/', selectGroup, name='getSelectGroup_url'),
    path('selectAttibutes/', selectAttibutes, name='getSelectAttribute_url'),
    path('selectWOs/', selectWOs, name='getSelectWOs_url'),
    path('addWorkOrder/', addWorkOrder, name='addWorkOrder_url'),




    path('ssData/', saveSessionState, name='saveSessionState_url'),            
    path('saveItem/', saveItem, name='saveItem_url'),
    path('saveComment/', saveComment, name='saveComment_url'),
    path('saveCalendar/', saveCalendar, name='saveCalendar_url'),
    path('saveQuote/', saveQuote, name='saveQuote_url'),
    path('saveMaterial/', saveMaterial, name='saveMaterial_url'),
    path('saveWO/', saveWO, name='saveWO_url'),

    path('updateStatus/', updateStatus, name='updateStatus_url'),


    
    path('deleteItem/', deleteItem, name='deleteItem_url'),
    path('deleteProyect/', deleteProyect, name='deleteProyect_url'),
    path('deleteItemCommentFile/', deleteItemCommentFile, name='deleteItemCommentFile_url'),
    path('deleteComment/', deleteComment, name='deleteComment_url'),
    path('deleteCommentCalendar/', deleteCommentCalendar, name='deleteCommentCalendar_url'),
    path('deleteFile/', deleteFile, name='deleteFile_url'),
    path('deleteTaskCalendar/', deleteTaskCalendar, name='deleteTaskCalendar_url'),
                

]
