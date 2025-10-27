from django.contrib import messages
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib.auth.decorators import login_required #para controlar las sesiones

# from datetime import datetime # dar formato a la fecha
# from django.utils import timezone #Para ver la hora correctamente.


from ..models import Item, Proyect, ItemCommentState, WorkOrderCommentState, CalendarItemComment, CalendarWorkOrderComment, CalendarTaskComment, ItemCommentStateFile, WorkOrderCommentStateFile, ItemImage, ItemFile, ItemMaterial, CalendarTask, WorkOrder
from ..utils.utils import saveEvent


#Funcion ejecutada en la vista del proyecto, para borrar un item específico.
@login_required
def deleteItem(request):
    item_id = request.POST.get('i') 
    status = 0

    try:
        item = Item.objects.get(id = item_id)
        saveEvent(request, 3, item.workorder.proyect, item.workorder, item, item.code + ': ' + item.subcategory.category.name)
        item.delete()
        status = 1
        

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


#Funcion ejecutada en el panel, para borrar un proyecto en particular.
@login_required
def deleteProyect(request):
    proyect_id = request.POST.get('p')
    status = 0
    title = ''
    message = ''

    try:

        if request.user.is_superuser:
            proyect = Proyect.objects.get(id = proyect_id)
            saveEvent(request, 3, proyect, None, None, 'Address : ' + proyect.customer.address)
            proyect.delete()
            status = 1
            title = 'Deleted!'
            message = 'The proyect has been successfully deleted.'

        else:
            status = 1
            title = 'Access denied!'
            message = 'Administrator privileges required.'

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status, 'title': title, 'message': message})


#Funcion ejecutada en los comentarios, para ser eliminados del sistema
@login_required
def deleteComment(request):    
    itemCommentId = request.POST.get('t')
    itemId = request.POST.get('e')
    workorderId = request.POST.get('w')
    status = 0

    try:
        #Si es un item específico
        if int(itemId) != 0:

            itemCS = ItemCommentState.objects.get(id = itemCommentId)            

            if itemCS.item.workorder.id == int(workorderId) and itemCS.item.id == int(itemId): #Si pertenece al wo-item, se borra
                itemCS.delete()        
                status = 1
            else:
                status = 2
        
        #Si es un comentario genérico
        else:

            itemCS = WorkOrderCommentState.objects.get(id = itemCommentId)            

            if itemCS.workorder.id == int(workorderId): #Si pertenece a la wo, se borra
                itemCS.delete()        
                status = 1
            else:
                status = 2            

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


#Funcion ejecutada para eliminar comentarios del calendario
@login_required
def deleteCommentCalendar(request):        
    workorderId = request.POST.get('w')
    itemId = request.POST.get('t')
    id = request.POST.get('i')
    status = 0

    try:
        #Si es un item 
        if itemId != '0':

            comment = CalendarItemComment.objects.filter(id = id)
            if comment:
                comment.delete()
        
        #Si es una wo
        elif workorderId != '0':

            comment = CalendarWorkOrderComment.objects.filter(id = id)
            if comment:
                comment.delete()

        #Si es una wo
        elif itemId == '0' and workorderId == '0':

            comment = CalendarTaskComment.objects.filter(id = id)
            if comment:
                comment.delete()

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')
 
    return JsonResponse({'result': status})


#Funcion ejecutada a la hora de borrar un archivo de un comentario.
@login_required
def deleteItemCommentFile(request):
    id = request.POST.get('i') 
    itemCstId = request.POST.get('t')
    itemId = request.POST.get('e')
    workOrderId = request.POST.get('w')
    status = 0

    try:

        if int(itemId) != 0:

            itemCS = ItemCommentState.objects.get(id = itemCstId)
            itemCSF = ItemCommentStateFile.objects.get(id = id, item_comment_state = itemCS)

            if itemCSF.item_comment_state.item.workorder.id == int(workOrderId) and itemCSF.item_comment_state.item.id == int(itemId): #Si pertenece al wo-item, se borra
                itemCSF.delete()        
                status = 1
            else:
                status = 2

        else:

            itemCS = WorkOrderCommentState.objects.get(id = itemCstId)
            itemCSF = WorkOrderCommentStateFile.objects.get(id = id, workorder_comment_state = itemCS)

            if itemCSF.workorder_comment_state.workorder.id == int(workOrderId) and itemCSF.workorder_comment_state.workorder.id == int(workOrderId): #Si pertenece a la wo, se borra
                itemCSF.delete()        
                status = 1
            else:
                status = 2        

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


#Funcion ejecutada para eliminar una imagen o material adjunto al item.
@login_required
def deleteFile(request):
    itemId = request.POST.get('i')
    fileId = request.POST.get('f')    
    status = 0
    item = None

    try:
        
        if int(itemId) != 0:
            item = Item.objects.get(id = itemId)

        pre = fileId.split('_')[0] 
        id = fileId.split('_')[1] 

        if pre == 'IMG':                    
            itemFile = ItemImage.objects.get(id = id, item = item)

            if itemFile: #Si pertenece al item, se borra
                itemFile.delete()        
                status = 1
            else:
                status = 2

        if pre == 'FIL':
            itemFile = ItemFile.objects.get(id = id, item = item)

            if itemFile: #Si pertenece al item, se borra
                itemFile.delete()        
                status = 1
            else:
                status = 2

        if pre == 'MAT':
            itemFile = ItemMaterial.objects.get(id = id, item = item)

            if itemFile: #Si pertenece al item, se borra
                itemFile.delete()        
                status = 1
            else:
                status = 2


    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


#Funcion ejecutada para eliminar tareas del calendario
@login_required
def deleteTaskCalendar(request):            
    id = request.POST.get('i')
    status = 0

    try:
        task = CalendarTask.objects.filter(id = id)
        if task:
            task.delete()
            status = 1

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')
 
    return JsonResponse({'result': status})


#Funcion ejecutada en la vista del proyecto, para borrar una wo específico.
@login_required
def deleteWO(request):
    wo_id = request.POST.get('w') 
    status = 0

    try:
        workorder = WorkOrder.objects.get(id = wo_id)
        saveEvent(request, 3, workorder.proyect, workorder, None, workorder.code + ': ' + workorder.proyect.customer.address)
        workorder.delete()
        status = 1
        

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})

