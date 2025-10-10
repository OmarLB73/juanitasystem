import requests
from django.conf import settings
from django.core.exceptions import ValidationError #Para manejar excepciones
from django.utils import timezone #Para ver la hora correctamente.
from django.contrib.auth.models import User #Datos del usuario
from collections import defaultdict
from datetime import datetime, timedelta
from django.contrib import messages

from ..models import State, WorkOrder, Event, Proyect, Responsible, CalendarItem, CalendarItemComment, CalendarWorkOrder, CalendarWorkOrderComment, CalendarTask, CalendarTaskComment, CalendarItemCommentFile, CalendarWorkOrderCommentFile, CalendarTaskCommentFile


#Funcion usada para validar tipos de archivos
def validateTypeFile(value):

    isfileValidate = False

    try:                
        # Tipos permitidos
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg', 'image/bmp','image/mpo','application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.ms-powerpoint','application/vnd.openxmlformats-officedocument.presentationml.presentation']

        if value in tipos_permitidos:            
            isfileValidate = True

    except IOError:
        # raise ValidationError(f'El archivo debe ser una imagen de tipo: {", ".join(tipos_permitidos)}')
        raise ValidationError("El archivo no es una imagen válida.")
    
    return isfileValidate


#Retorna el % de avance del proyecto
def retornAdvance(value):

    adv = 0
    factor = 11 #11.11
    adv = value * factor
    
    return adv

#Retorna la tabla html con los datos del decorador/ayudante
def getDecoratorsTable(decorators):
    
    # Creamos una lista con los datos de cada proyecto

    decoratorsHTML = ''

    if len(decorators) > 0:

        #decoratorsHTML = '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-7 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
        decoratorsHTML = '<div class="table-responsive"><table class="table table-striped"><thead class="border-bottom border-gray-200 fs-7 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
        decoratorsHTML += '<th title="Field #1" class="p-2">Name</th>'
        decoratorsHTML += '<th title="Field #3">Phone</th>'
        decoratorsHTML += '<th title="Field #2">Email</th>'        
        decoratorsHTML += '<th title="Field #4">Address</th>'
        decoratorsHTML += '<th title="Field #5">Apt-ste-floor</th>'
        decoratorsHTML += '<th title="Field #6">City</th>'
        decoratorsHTML += '<th title="Field #7">State</th>'
        decoratorsHTML += '<th title="Field #8">Zipcode</th>'
        
        decoratorsHTML += '</tr></thead><tbody>'

        for decorator in decorators:  

            name = decorator.name if decorator.name  else " "
            phone = decorator.phone if decorator.phone  else " "
            email = decorator.email if decorator.email  else " "
            address = decorator.address if decorator.address  else " "
            apartment = decorator.apartment if decorator.apartment  else " "
            city = decorator.city if decorator.city  else " "
            state = decorator.state if decorator.state  else " "
            zipcode = decorator.zipcode if decorator.zipcode  else " "

            decoratorsHTML += '<tr>'
            decoratorsHTML += '<td class="text-start fs-7 p-2">' + str(name) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(phone) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(email) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(address) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(apartment) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(city) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(state) + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + str(zipcode) + '</td>'
            decoratorsHTML += '</tr>'
        
        decoratorsHTML += '</tbody></table></div>'

    return decoratorsHTML


#Retorna el nombre del estado, junto con su clase css
def getStateName(stateId, case): #case: WO - comments table
    
    state = State.objects.get(id = stateId)

    name = state.name
    description = state.description

    stateHTML = ''

    #stateHTML += '<i class="fas fa-question-circle" data-bs-toggle="tooltip" title="' + description + '"></i>'

    if case == "WO":
        stateHTML += '<span class="fs-6 fw-bold p-2 badge-state-' + str(stateId) + '">'
        stateHTML += name
        stateHTML += '</span>'
    elif case == "TC":
        stateHTML += '<div class="fs-7 fw-bold p-2 badge-state-' + str(stateId) + '">'
        stateHTML += name
        stateHTML += '</div>'
    else:
        stateHTML += '<th style="width: 90px; max-width: 90px; padding: 0;"><div class="badge-state-' + str(stateId) + ' p-1" style="width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 10px; text-align: center;" title="' + name + '" >'
        stateHTML += name
        stateHTML += '</div></th>'

    return stateHTML																									



#Retorna resumen WO´s
def getResumenWOs(request, proyect):

    state = None

    try: 
        if 'stateId' in request.session:
            state = State.objects.filter(id = request.session['stateId']).first()         
    except:
        None

    if state:
        wos = WorkOrder.objects.filter(proyect = proyect, status=1, state = state).order_by('-id')
    else:
        wos = WorkOrder.objects.filter(proyect = proyect, status=1).order_by('-id')

    # Obtener eventos relevantes
    eventos = Event.objects.filter(type_event_id__in=(1,2), workorder__in = wos, item = None).select_related('workorder', 'state')
    # Crear estructura: workorder_id -> { state_id -> fecha }
    pivot_data = defaultdict(lambda: defaultdict(lambda: None))
    # Recorrer eventos y guardar la última fecha por estado por workorder
    for evento in eventos:
        if evento.workorder and evento.state:
            current = pivot_data[evento.workorder.id][evento.state.id]
            if not current or evento.creation_date > current:
                pivot_data[evento.workorder.id][evento.state.id] = evento.creation_date


    states = State.objects.filter(status = 1).order_by('id')

    html = '<div class="table-responsive"><table class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"><thead><tr><th style="width:80px; max-width:80px;"></th>'

    for state in states:

        html += getStateName(state.id, "")
        if state.id != 10:
            html += '<th style="max-width:2%; padding:3px" class="text-center">Ant</th>'
        else:
            html += '<th style="max-width:2%; padding:3px" class="text-center">Total</th>'

    html += '</tr></thead><tbody>'


    # Cuerpo
    for wo in wos:
        html += f'<tr><th class="fs-20 fw-bold"><b>WO-{wo.code}</b></th>'

        fechas_validas = []  # Aquí guardaremos todas las fechas válidas
        prev_fecha = None
                
        for state in states:
            # Fecha actual para este estado y workorder
            fecha = pivot_data.get(wo.id, {}).get(state.id)
            fecha_str = timezone.localtime(fecha).strftime("%b %d, %Y") if fecha else ''                                  
            
            diff_str = ''

            if fecha:
                fechas_validas.append(fecha)

            # Solo calcular diferencia si el estado no es 1
            if state.id != 1:
                # Calcular diferencia con la fecha anterior
                if fecha and prev_fecha:
                    diferencia_dias = (fecha - prev_fecha).days
                    diff_str = f'{diferencia_dias}'                

                # Escribir celdas: fecha + Ant
                html += f'<td class="fs-16"><span class="text-muted">{diff_str}</span></td>'
                html += f'<td class="fs-16">{fecha_str}</td>'
            else:
                # Solo escribimos 1 celda si state.id == 10
                html += f'<td>{fecha_str}</td>'

            # Actualizar fecha anterior solo si existe
            if fecha:
                prev_fecha = fecha

        # Total entre primera y última fecha válida
        if len(fechas_validas) >= 2:
            fecha_inicio = min(fechas_validas)
            fecha_fin = max(fechas_validas)
            total = (fecha_fin - fecha_inicio).days
        else:
            total = 0

        html += f'<td><span class="text-muted">{total}</span></td>'

        html += '</tr>'

    html += '</tbody></table></div>'

    return html




#Funcion para crear una nueva WO
def newWO(request, proyectId):

    try:

        proyect = Proyect.objects.get(id = proyectId)
        workorder = WorkOrder.objects.create(  proyect = proyect,
                                                state = State.objects.get(id = 1),                                                        
                                                created_by_user = request.user.id,
                                                modification_by_user = request.user.id)

        workorder.save()

        saveEvent(request, 1, proyect, workorder, None, 'Create WO')

        return workorder
        
    except:
        return None


def _obsoleto_timeline_body(date_str, name, email, description, stateId):
    
    timeline_cont = '<div class="timeline-content mb-10 mt-n1">'    
    timeline_cont += '<div class="mb-5 pe-3">'
    
    if stateId == 1:
        timeline_cont += '<div class="fs-6 fw-bold mb-2 badge-light-success">' + description + '</div>'
    elif stateId == 6:
        timeline_cont += '<div class="fs-6 fw-bold mb-2 badge-light-success">' + description + '</div>'
    else:
        timeline_cont += '<div class="fs-6 fw-bold mb-2">' + description + '</div>'
        
    timeline_cont += '<div class="d-flex align-items-center mt-1 fs-6">'
    
    timeline_cont += '<div class="text-muted me-2 fs-7">' + date_str + '</div>'    
    timeline_cont += '<div class="symbol symbol-circle symbol-25px" data-bs-toggle="tooltip" data-bs-boundary="window" data-bs-placement="top" title="' + name + '">'    
    timeline_cont += '<div class="text-primary fw-bolder me-1"> ' + email +'</div>'

    timeline_cont += '</div>'
    timeline_cont += '</div>'
    timeline_cont += '</div>'
    timeline_cont += '</div>'

    return timeline_cont


def htmlResponsibleSelect(responsable_id):

    if responsable_id == None:
        responsable_id = 0

    html = '<option value="0" data-color="gris" selected></option>'
    
    responsibles = Responsible.objects.filter(status = 1).order_by('name')

    for responsible in responsibles:
        if responsable_id == responsible.id:
            html += '<option value=' + str(responsible.id) + ' data-color="' + str(responsible.color) + '" selected>' + responsible.name + '</option>'
        else:                
            html += '<option value=' + str(responsible.id) + ' data-color="' + str(responsible.color) + '">' + responsible.name + '</option>'
            
    return html


def htmlStatusCalendar(status_Id, date, obj, name):

    html = '<select class="form-select form-select-sm form-select-solid" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="' + name + '" >'
    
    if date != '':
            
    # if obj is None or date == '':
    #     if date == '':    
    #         html += '<option value="-1" selected>---</option>'
    #     else:
    #         html += '<option value="-1">---</option>'    
    
        if status_Id == 1:    
            html += '<option value="1" selected>Active</option>'
        else:
            html += '<option value="1">Active</option>'

        if status_Id == 0:    
            html += '<option value="0" selected>Inactive</option>'
        else:
            html += '<option value="0">Inactive</option>'

        if status_Id == 2:    
            html += '<option value="2" selected>Completed</option>'
        else:
            html += '<option value="2">Completed</option>'                

    else:
        html += '<option value="1">Active</option>'  # Debe retornar por lo menos una opción, si o si.

    html += '</select>'
            
    return html


def htmlSpanCalendar():

    html = '<span class="svg-icon position-relative">'
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    html += '<path opacity="0.3" d="M21 22H3C2.4 22 2 21.6 2 21V5C2 4.4 2.4 4 3 4H21C21.6 4 22 4.4 22 5V21C22 21.6 21.6 22 21 22Z" fill="black" />'
    html += '<path d="M6 6C5.4 6 5 5.6 5 5V3C5 2.4 5.4 2 6 2C6.6 2 7 2.4 7 3V5C7 5.6 6.6 6 6 6ZM11 5V3C11 2.4 10.6 2 10 2C9.4 2 9 2.4 9 3V5C9 5.6 9.4 6 10 6C10.6 6 11 5.6 11 5ZM15 5V3C15 2.4 14.6 2 14 2C13.4 2 13 2.4 13 3V5C13 5.6 13.4 6 14 6C14.6 6 15 5.6 15 5ZM19 5V3C19 2.4 18.6 2 18 2C17.4 2 17 2.4 17 3V5C17 5.6 17.4 6 18 6C18.6 6 19 5.6 19 5Z" fill="black" />'
    html += '<path d="M8.8 13.1C9.2 13.1 9.5 13 9.7 12.8C9.9 12.6 10.1 12.3 10.1 11.9C10.1 11.6 10 11.3 9.8 11.1C9.6 10.9 9.3 10.8 9 10.8C8.8 10.8 8.59999 10.8 8.39999 10.9C8.19999 11 8.1 11.1 8 11.2C7.9 11.3 7.8 11.4 7.7 11.6C7.6 11.8 7.5 11.9 7.5 12.1C7.5 12.2 7.4 12.2 7.3 12.3C7.2 12.4 7.09999 12.4 6.89999 12.4C6.69999 12.4 6.6 12.3 6.5 12.2C6.4 12.1 6.3 11.9 6.3 11.7C6.3 11.5 6.4 11.3 6.5 11.1C6.6 10.9 6.8 10.7 7 10.5C7.2 10.3 7.49999 10.1 7.89999 10C8.29999 9.90003 8.60001 9.80003 9.10001 9.80003C9.50001 9.80003 9.80001 9.90003 10.1 10C10.4 10.1 10.7 10.3 10.9 10.4C11.1 10.5 11.3 10.8 11.4 11.1C11.5 11.4 11.6 11.6 11.6 11.9C11.6 12.3 11.5 12.6 11.3 12.9C11.1 13.2 10.9 13.5 10.6 13.7C10.9 13.9 11.2 14.1 11.4 14.3C11.6 14.5 11.8 14.7 11.9 15C12 15.3 12.1 15.5 12.1 15.8C12.1 16.2 12 16.5 11.9 16.8C11.8 17.1 11.5 17.4 11.3 17.7C11.1 18 10.7 18.2 10.3 18.3C9.9 18.4 9.5 18.5 9 18.5C8.5 18.5 8.1 18.4 7.7 18.2C7.3 18 7 17.8 6.8 17.6C6.6 17.4 6.4 17.1 6.3 16.8C6.2 16.5 6.10001 16.3 6.10001 16.1C6.10001 15.9 6.2 15.7 6.3 15.6C6.4 15.5 6.6 15.4 6.8 15.4C6.9 15.4 7.00001 15.4 7.10001 15.5C7.20001 15.6 7.3 15.6 7.3 15.7C7.5 16.2 7.7 16.6 8 16.9C8.3 17.2 8.6 17.3 9 17.3C9.2 17.3 9.5 17.2 9.7 17.1C9.9 17 10.1 16.8 10.3 16.6C10.5 16.4 10.5 16.1 10.5 15.8C10.5 15.3 10.4 15 10.1 14.7C9.80001 14.4 9.50001 14.3 9.10001 14.3C9.00001 14.3 8.9 14.3 8.7 14.3C8.5 14.3 8.39999 14.3 8.39999 14.3C8.19999 14.3 7.99999 14.2 7.89999 14.1C7.79999 14 7.7 13.8 7.7 13.7C7.7 13.5 7.79999 13.4 7.89999 13.2C7.99999 13 8.2 13 8.5 13H8.8V13.1ZM15.3 17.5V12.2C14.3 13 13.6 13.3 13.3 13.3C13.1 13.3 13 13.2 12.9 13.1C12.8 13 12.7 12.8 12.7 12.6C12.7 12.4 12.8 12.3 12.9 12.2C13 12.1 13.2 12 13.6 11.8C14.1 11.6 14.5 11.3 14.7 11.1C14.9 10.9 15.2 10.6 15.5 10.3C15.8 10 15.9 9.80003 15.9 9.70003C15.9 9.60003 16.1 9.60004 16.3 9.60004C16.5 9.60004 16.7 9.70003 16.8 9.80003C16.9 9.90003 17 10.2 17 10.5V17.2C17 18 16.7 18.4 16.2 18.4C16 18.4 15.8 18.3 15.6 18.2C15.4 18.1 15.3 17.8 15.3 17.5Z" fill="black" />'
    html += '</svg>'
    html += '</span>'

    return html


def htmlDivCommentCalendar():
    html = '<div id="divComments">'
    #html += '<a href="javascript:void(0);" id="addComment">Add comment (+)</a>'
    html += '<table id="tableComments" class="table table-row-dashed table-row-gray-300 align-middle gs-0 gy-4">' # Estaba en style="display:none"
    html += '<thead class="fw-bolder text-muted">'
    html += '<tr>'
    html += '<th class="align-top" width="50%">Comment</th>'    
    html += '<th class="align-top" width="45%">Select file (optional)</th>'    
    html += '<th class="align-top" width="5%"></th>'
    html += '</tr>'
    html += '</thead>'
    html += '<tbody>'
    html += '<tr class="baseRowComment">' # Estaba en style="display:none"
    html += '<td valign="top"><textarea name="comment[]" class="form-control form-control-solid h-80px textareaComment" maxlength="2000"></textarea></td>'
    html += '<td valign="top" class="text-center"><input type="file" name="commentFile[]" class="form-control form-control"><input type="hidden" name="commentFileOk[]"></td>'
    html += '<td valign="top" class="text-center">'
    html += '<div class="btn btn-icon btn-sm btn-color-gray-400 btn-active-icon-danger me-2 deleteCommentCalendar" data-bs-toggle="tooltip" data-bs-dismiss="click" title="Delete">'
    html += '<span class="svg-icon svg-icon-2">'
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    html += '<path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" />'
    html += '<path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" />'
    html += '<path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" />'
    html += '</svg>'
    html += '</span>'
    html += '</div>'
    html += '</td>'
    html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    html += '</div>'

    return html


#Consulta realizada para obtener los datos de cada uno de los comentarios para el calendario.
def htmlDataCommentCalendar(request, workorder, item, task, mode): # mode 1: edicion, 2: lectura

    
    itemsHTML = ''
    itemTxt = ''
    itemsHTML += '<div class="col-xl-12 fv-row text-start" style="max-height: 200px; overflow: auto;">'
    calendar = None
    comments = None
    workorderId = 0
    itemId = 0

    if item:
        calendar = CalendarItem.objects.filter(item = item).first()
        comments = CalendarItemComment.objects.filter(calendar_item = calendar).order_by('-id')
        itemId = item.id
    elif workorder:
        calendar = CalendarWorkOrder.objects.filter(workorder = workorder).first()
        comments = CalendarWorkOrderComment.objects.filter(calendar_workorder = calendar).order_by('-id')
        workorderId = workorder.id
    elif task:
        calendar = CalendarTask.objects.filter(id = task).first()
        comments = CalendarTaskComment.objects.filter(calendar_task = calendar).order_by('-id')
    
        
    # itemsHTML += '<h7><b>Comments:</b></h7>'

    if len(comments) > 0:

        itemsHTML += '<table class="table table-rounded table-striped"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Date</th><th width="10%">Time</th><th width="20%">User</th><th width="55%">Notes</th>'

        if mode == 1:
            itemsHTML += '<th width="5%"></th>'

        itemsHTML += '</tr></thead><tbody>'
    
        for comment in comments:                        
            date = ''
            time = ''            
            username = ''
            itemTxt = ''

            if comment.notes:
                itemTxt = comment.notes

            if comment.modification_date:
                date = timezone.localtime(comment.modification_date).strftime('%m/%d/%Y')
                time = timezone.localtime(comment.modification_date).strftime('%H:%M %p')

    
            user = User.objects.get(id=comment.modification_by_user)

            if user:
                username = user.username

            files = None
            
            if item:
                files = CalendarItemCommentFile.objects.filter(calendar_item_comment = comment)
            elif workorder:
                files = CalendarWorkOrderCommentFile.objects.filter(calendar_workorder_comment = comment)
            elif task:
                files = CalendarTaskCommentFile.objects.filter(calendar_task_comment = comment)

            if files:            
                itemTxt += '<ul class="text-start py-1">'
            
                for file in files:                    
                    itemTxt += '<li><a href=' + file.file.url + ' target="_blank">' + file.name + '</a>'
            
                itemTxt += "</ul>"


            itemsHTML += '<tr class="py-0 fw-bold fs-7"><td>' + date + '</td><td>' + time + '</td><td>' + username + '</td><td>' + itemTxt + '</td>'

            user_session = request.user
                        
            if user == user_session and mode == 1: #edicion
                itemsHTML += '<td><a href="#" class="py-0 btn btn-link fs-7" onclick="delCommCalendar(' + str(workorderId) + ',' + str(itemId) + ',' + str(comment.id) + ',event, this)"><span class="svg-icon svg-icon-3" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" /><path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" /><path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" /></svg></span></a></td>'
            else:
                itemsHTML += '<td></td>'

            itemsHTML += '</tr>'
    
        itemsHTML += '</tbody></table>'

    itemsHTML += '</div>'

    return itemsHTML


def htmlDivCollapse(name, id, title, mode):
    divHTML = ''

    if mode == 1:
        divHTML += '<div class="d-flex align-items-center collapsible py-3 toggle collapsed mb-0" data-bs-toggle="collapse" data-bs-target="#' + str(name) + '_' + str(id) + '">'
    if mode == 2:
        divHTML += '<div class="d-flex align-items-center collapsible py-3 toggle mb-0" data-bs-toggle="collapse" data-bs-target="#' + str(name) + '_' + str(id) + '">'

    divHTML += '<div class="btn btn-sm btn-icon btn-active-color-primary">'
    
    divHTML += '<span class="svg-icon toggle-on svg-icon-primary svg-icon-1">'
    divHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    divHTML += '<rect opacity="0.3" x="2" y="2" width="20" height="20" rx="5" fill="black"></rect>'
    divHTML += '<rect x="6.0104" y="10.9247" width="12" height="2" rx="1" fill="black"></rect>'
    divHTML += '</svg>'
    divHTML += '</span>'
    
    divHTML += '<span class="svg-icon toggle-off svg-icon-1">'
    divHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    divHTML += '<rect opacity="0.3" x="2" y="2" width="20" height="20" rx="5" fill="black"></rect>'
    divHTML += '<rect x="10.8891" y="17.8033" width="12" height="2" rx="1" transform="rotate(-90 10.8891 17.8033)" fill="black"></rect>'
    divHTML += '<rect x="6.01041" y="10.9247" width="12" height="2" rx="1" fill="black"></rect>'
    divHTML += '</svg>'
    divHTML += '</span>'

    divHTML += '</div>'

    divHTML += '<h7 class="cursor-pointer mb-0"><b>' + title + '</b></h7>'

    divHTML += '</div>'
    
    if mode == 1:
        divHTML += '<div id="' + str(name) + '_' + str(id) + '" class="row fs-7 ms-1 collapse">' # style="border:1px solid white; border-width:1px;"
    if mode == 2:
        divHTML += '<div id="' + str(name) + '_' + str(id) + '" class="row fs-7 ms-1 collapse show">' #style="border:1px solid white; border-width:1px;"
    

    divHTML += '<div class="row">' # style="border:1px solid white; border-width:1px;"

    return divHTML


#Consulta realizada para obtener los últimos eventos
def htmlDataLog(request): # mode 1: edicion, 2: lectura
    
    eventHTML = ''


    iconNewProyect = '<div class="timeline-icon symbol symbol-circle symbol-40px"><div class="symbol-label bg-light"> <span class="svg-icon svg-icon-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="black" stroke-width="2"> <path stroke-linecap="round" stroke-linejoin="round" d="M12 11c1.104 0 2-.896 2-2s-.896-2-2-2-2 .896-2 2 .896 2 2 2z"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 21c-4-3.5-7-7.5-7-11a7 7 0 1 1 14 0c0 3.5-3 7.5-7 11z"/></svg></span>  </div></div>'
    iconNewWO = '<div class="timeline-icon symbol symbol-circle symbol-40px"><div class="symbol-label bg-light"> <span class="svg-icon svg-icon-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="black" stroke-width="2">     <rect x="9" y="2" width="6" height="6" rx="1" ry="1" /><path stroke-linecap="round" stroke-linejoin="round" d="M13 10H7a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3"/></svg></span>  </div></div>'
    iconNewItem = '<div class="timeline-icon symbol symbol-circle symbol-40px me-4"><div class="symbol-label bg-light"> <span class="svg-icon svg-icon-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"  viewBox="0 0 24 24" stroke="black" stroke-width="2"><rect x="3" y="7" width="18" height="10" rx="2" ry="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M3 7l9 5 9-5"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 12v7"/></svg></span>  </div></div>'
    

    iconEdit = '<div class="timeline-icon symbol symbol-circle symbol-40px"><div class="symbol-label bg-light"> <span class="svg-icon svg-icon-2 text-primary"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="black" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg></span>  </div></div>'
    iconDelete = '<div class="timeline-icon symbol symbol-circle symbol-40px"><div class="symbol-label bg-light"> <span class="svg-icon svg-icon-2 svg-icon-gray-500" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M6 7H18M9 7V5C9 4.44772 9.44772 4 10 4H14C14.5523 4 15 4.44772 15 5V7M10 11V17M14 11V17M5 7H19L18.2929 19.2929C18.1054 21.0503 16.636 22.5 14.8726 22.5H9.12742C7.36401 22.5 5.89464 21.0503 5.70711 19.2929L5 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> </span></div></div>'
    
    try:
    
        events = Event.objects.order_by('-creation_date')[:30]

        for event in events:    
            
            eventHTML += '<div class="timeline-item">'
            eventHTML += '<div class="timeline-line w-40px"></div>'
            title = ''
            subtitle = ''
            address = ''
            userName = ''
            date = timezone.localtime(event.creation_date).strftime("%B %d, %Y at %I:%M %p")

            if event.proyect:

                if event.proyect.customer:

                    if event.proyect.customer.address:
                        address += '<b>' + event.proyect.customer.address + '</b>'

                    if event.proyect.customer.city:
                        address += ',' + event.proyect.customer.city

                    if event.proyect.customer.state:
                        address += ',' + event.proyect.customer.state

                    if event.proyect.customer.zipcode:
                        address += ',' + event.proyect.customer.zipcode

                    if event.proyect.customer.apartment:
                        address += ',' + event.proyect.customer.apartment

                    if event.proyect.id:
                        address += ' (<a href="/proyect/view/' + str(event.proyect.id)  + '" class="text-primary fw-bolder me-1">#' + str(event.proyect.id)  + '</a>)'                        

            if event.user:
                creator = User.objects.filter(id = event.user).first()

                if creator:
                    userName = '<div class="symbol symbol-circle symbol-25px" data-bs-toggle="tooltip" data-bs-boundary="window" data-bs-placement="top" title="' + creator.first_name + ' ' + creator.last_name + '"> <a href="#" class="text-primary fw-bolder me-1">' + creator.username + '</a></div>'
                        
                    
            ## Create
            if event.type_event_id == 1 and event.proyect and event.workorder is None:
                eventHTML += iconNewProyect
                title += 'A new project has been created: ' + address            

            elif event.type_event_id == 1 and event.workorder and event.item is None:
                eventHTML += iconNewWO
                title = 'A new work order has been created for the address: ' + address

            elif event.type_event_id == 1 and event.workorder and event.item:
                eventHTML += iconNewItem
                title = 'A new item has been created for the address: ' + address

            
            ## Edit
            elif event.type_event_id == 2 and event.workorder and event.item is None:
                eventHTML += iconEdit
                title = 'A work order has been updated for the address: ' + address

                if event.workorder.code and event.description:

                    subtitle += '<div class="overflow-auto pb-3">'
                    subtitle += '<div class="notice d-flex bg-light-primary rounded border-primary border border-dashed min-w-lg-600px flex-shrink-0 p-6">'
                    subtitle += '<span class="svg-icon svg-icon-2tx svg-icon-primary me-4">'
                    subtitle += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M19.0687 17.9688H11.0687C10.4687 17.9688 10.0687 18.3687 10.0687 18.9688V19.9688C10.0687 20.5687 10.4687 20.9688 11.0687 20.9688H19.0687C19.6687 20.9688 20.0687 20.5687 20.0687 19.9688V18.9688C20.0687 18.3687 19.6687 17.9688 19.0687 17.9688Z" fill="black" /><path d="M4.06875 17.9688C3.86875 17.9688 3.66874 17.8688 3.46874 17.7688C2.96874 17.4688 2.86875 16.8688 3.16875 16.3688L6.76874 10.9688L3.16875 5.56876C2.86875 5.06876 2.96874 4.46873 3.46874 4.16873C3.96874 3.86873 4.56875 3.96878 4.86875 4.46878L8.86875 10.4688C9.06875 10.7688 9.06875 11.2688 8.86875 11.5688L4.86875 17.5688C4.66875 17.7688 4.36875 17.9688 4.06875 17.9688Z" fill="black" /></svg>'
                    subtitle += '</span>'
                                                                                        
                    subtitle += '<div class="d-flex flex-stack flex-grow-1 flex-wrap flex-md-nowrap">'
                    subtitle += '<div class="mb-3 mb-md-0 fw-bold">'

                    if event.workorder.code:
                        subtitle += '<h7 class="text-gray-900 fw-bolder">Work Order ' + event.workorder.code + '</h7>'

                    if event.description:
                        subtitle += '<div class="fs-7 text-gray-700 pe-7">' + event.description + '</div>'

                    subtitle += '</div>'
                    
                    
                    if event.workorder.state:
                        if event.workorder.state.id >= 5:            
                            subtitle += '<a href="/proyect/generate_pdf/' + str(event.workorder.id)  + '" class="btn btn-sm btn-primary px-6 align-self-center text-nowrap" target="_blank">View WO</a>'
                    
                    subtitle += '</div>'
                    subtitle += '</div>'
                    subtitle += '</div>'


            elif event.type_event_id == 2 and event.workorder and event.item:
                eventHTML += iconEdit
                title = 'A item has been updated for the address: ' + address            


            ## Delete
            elif event.type_event_id == 3 and event.proyect is None:
                eventHTML += iconDelete
                title += 'A project has been deleted'

                if event.description:
                    if event.description != '':
                        title += ': ' + event.description
            
            elif event.type_event_id == 3 and event.proyect and event.workorder is None:
                eventHTML += iconDelete
                title += 'A work order has been deleted'

                if event.description:
                    if event.description != '':
                        title += ': ' + event.description

            elif event.type_event_id == 3 and event.proyect and event.workorder and event.item is None:
                eventHTML += iconDelete
                title += 'A item has been deleted'

                if event.description:
                    if event.description != '':
                        title += ': ' + event.description


            #### 

            if title != '':
            
                eventHTML += '<div class="timeline-content mb-10 mt-n2">'
                eventHTML += '<div class="pe-3 mb-5">'
                eventHTML += '<div class="fs-7 fw-bold mb-2">'
                eventHTML += title


                eventHTML += '<div class="d-flex align-items-center mt-1 fs-6">'
                eventHTML += '<div class="text-muted me-2 fs-7">This event occurred on ' + date
                
                if userName != '':
                    eventHTML += ' by ' + userName

                if subtitle != '':
                    eventHTML += '<br/><br/>' + subtitle
                
                eventHTML += '</div>'
                eventHTML += '</div>'


                eventHTML += '</div>'
                eventHTML += '</div>'
                eventHTML += '</div>'

            #### 

            eventHTML += '</div>'

    except:
        pass
    

    return eventHTML


def enviar_notificacion_push(titulo, mensaje, user_ids):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "headings": {"en": titulo},
        "contents": {"en": mensaje},
        "include_external_user_ids": [str(uid) for uid in user_ids],
        "channel_for_external_user_ids": "push"
    }

    r = requests.post("https://onesignal.com/api/v1/notifications", json=payload, headers=headers)
    return r.status_code, r.json()


#Generar lista de horas
def getHours(intervalo=15):
    horas = []
    tiempo = datetime.strptime("00:00", "%H:%M")
    fin = datetime.strptime("23:45", "%H:%M")
    while tiempo <= fin:
        hora_24 = tiempo.strftime("%H:%M")      # para guardar en base de datos
        hora_12 = tiempo.strftime("%I:%M %p").lower()    # para mostrar al usuario
        horas.append((hora_24, hora_12))
        tiempo += timedelta(minutes=intervalo)
    return horas


#Generar select con la lista de horas
def getDateSelect(name='hora', id='hora-select', classAdd='', selected=None, checked=None):
    opciones = getHours()
    display = ''

    if checked:
        display = 'style="display:none"'

    html = f'<select name="{name}" id="{id}" class="form-select form-select-solid py-2 {classAdd}" data-control="select2" data-placeholder="Select a time" data-allow-clear="true" {display}>\n'
        
    for value, label in opciones:
        selected_attr = ' selected' if value == selected else ''
        html += f'  <option value="{value}"{selected_attr}>{label}</option>\n'
    
    html += '</select>'
    return html



#Instancia para guardar cada evento que ocurre en la WO.
def saveEvent(request, type_event_id, proyect, workOrder, item, description):

    # EVENTOS = [
        # (0, 'Other'),
        # (1, 'Create'),
        # (2, 'Update'),
        # (3, 'Delete'),    
    #     ]
    try:

        woState = None

        if workOrder:
            if workOrder.state:
                woState = workOrder.state

        Event.objects.create(   type_event_id=type_event_id,
                                proyect = proyect,                                    
                                workorder= workOrder, 
                                state = woState,
                                item = item,
                                description = description,
                                user=request.user.id)
        
    except Proyect.DoesNotExist:        
        messages.error('Server error. Please contact to administrator!')
    

