from django.contrib import messages
from django.db.models import Q, Count # Q permite realizar consultas complejas / Count permite agrupar consultas

from datetime import datetime
from django.utils import timezone #Para ver la hora correctamente.

from django.contrib.auth.models import User #Datos del usuario


from ..models import Proyect, ProyectDecorator, WorkOrder, Item, ItemMaterial, Event, CalendarItem, Responsible, CalendarItemComment, CalendarWorkOrderComment, CalendarTaskComment, CalendarItemCommentFile, CalendarWorkOrderCommentFile, CalendarTaskCommentFile,State, ItemAttribute,ItemAttributeNote, ItemFile, ItemImage, ItemCommentState, WorkOrderCommentState, ItemCommentStateFile, WorkOrderCommentStateFile, Customer, CalendarWorkOrder, CalendarTask
from ..utils.utils import validateTypeFile, htmlDivCollapse, getStateName, htmlResponsibleSelect, htmlStatusCalendar, htmlDivCommentCalendar, htmlDataCommentCalendar, htmlSpanCalendar, getDateSelect



#Consulta realizada desde el Panel
def getDataProyect(filters):

    filters21 = Q()
    filters22 = Q()
    filters21 &= Q(workorder__status = 1)
    filters22 &= Q(status = 1)
    
    for key, value in filters.children:
        if key == 'workorder__state__id':
            filters21 &= Q(workorder__state__id = value)
            filters22 &= Q(state__id = value)

    proyectsData = []

    #Se aplican los filtros o se traer las wo's por defecto
    if filters:
        proyects = Proyect.objects.filter(filters).filter(filters21).order_by('-id').distinct()
    else:
        proyects = Proyect.objects.all().filter(filters21).order_by('-id').distinct()
    
    dateNow = datetime.now()

    #Se recorre cada WO
    for proyect in proyects:
        
        allDay = False 

        #Se busca los datos de los decoradores        
        decorators = ProyectDecorator.objects.filter(proyects = proyect, is_supervisor = 1).order_by('name')
        decoratorsStr = ''

        for decorator in decorators:              
            decoratorsStr += decorator.name + ' '

        
        #Se busca las WO del proyecto
        # statesHTML = '<select class="form-select form-select-solid" data-kt-select2="false">'
        statesHTML = ''
        workordersStates = WorkOrder.objects.filter(proyect = proyect).filter(filters22).values('state__id', 'state__name').annotate(count=Count('state__id')).order_by('state__id')

        for wo in workordersStates:
            # statesHTML += '<option><span class="fw-bold p-2 mb-3 badge badge-state-' + str(wo['state__id']) + '">' + str(wo['state__name']) + ': ' + str(wo['count']) + '</span></option>'
            statesHTML += '<span class="fw-bold p-2 mb-3 badge badge-state-' + str(wo['state__id']) + ' a_proyectEdit" data-id2="' + str(wo['state__id']) + '" style="cursor: pointer;">' + str(wo['state__name']) + ': ' + str(wo['count']) + '</span><br/>'

        # statesHTML += '</select>'


        #Se busca los items de la WO, y se ordenan las categorias
        items = Item.objects.filter(workorder__in = WorkOrder.objects.filter(proyect = proyect).filter(filters22)).order_by('group__subcategory__category__name')
        categoryList = []
        categoryStr = ''
        
        for item in items:
            #Manejamos esta excepción puesto que no todos los items alcanzaron a tener su grupo
            try:
                if item.subcategory.category.name not in categoryList:
                    categoryList.append(item.subcategory.category.name)
            except:
                pass
        
        for category in categoryList:            
            categoryStr += category + ','

        categoryStr = categoryStr[:-1]        
        qty_items = workordersStates.count()

        #Se busca los materiales para dejarlos disponibles para una búsqueda rápida        
        materials = ItemMaterial.objects.filter(item__in = items).values_list('notes', flat=True) #flat=True: no devuelve una lista de tuplas, sino una lista plana
        # Convertir las notes únicos en un string
        materialsString = ", ".join(materials)        

        dateCreation = proyect.creation_date
        dateCreation = dateCreation.replace(tzinfo=None)
        dateNow = dateNow.replace(tzinfo=None)
        difference = dateNow - dateCreation

        proyectsData.append({
            'id': proyect.id,
            'customerName': proyect.customer.name,
            'address': proyect.customer.address,
            'city': proyect.customer.city,
            'state_u': proyect.customer.state,
            'zipcode': proyect.customer.zipcode,
            'apartment': proyect.customer.apartment,            
            'creationDate': dateCreation.strftime("%m/%d/%Y"),
            'email': proyect.customer.email,
            'statesHTML': statesHTML,
            'allDay': allDay,
            'difference': difference.days,
            'decorators': decoratorsStr,
            'qty_items': qty_items,
            'categories': categoryStr,
            'materials': materialsString
        })
    
    return proyectsData


#Consulta realizada en la vista del proyecto, para ver las WO´s
def getDataWOs(request, proyect_id, stateId, mode): # mode 1: edicion, 2: lectura

    proyect = Proyect.objects.get(id=proyect_id)
    workOrders = WorkOrder.objects.filter(proyect = proyect).order_by('-id')
    workOrdersHTML = ""

    buttonName = ''
    stateNewName = ''
    stateDescription = ''
    buttonDescription = ''
    woN = len(workOrders) + 1

    items = Item.objects.none() #Evita errores si el proyecto no tiene wos
            
    for wo in workOrders:
        
        woN = woN - 1

        items =  Item.objects.filter(workorder__in = workOrders, workorder__status = 1)

        if not request.session.get('stateId'):
            if not wo.code or wo.code != str(woN):
                wo.code = woN
                wo.save()
                
        if (wo.state.id == int(stateId) or int(stateId) == 0) and wo.status == 1:

            try:

                if mode == 1:

                    state = State.objects.get(id = wo.state.id)

                    if state:

                        buttonName = str(state.buttonName)
                        stateDescription = str(state.description)
                        buttonDescription = str(state.buttonDescription)

                    if wo.state.id <= 9: #Penultimo estado
                        stateNewName = State.objects.get(id = wo.state.id + 1).name
                                                
            except:
                pass


            workOrdersHTML += '<div class="row gy-5 g-xl-8">' #WO        
            workOrdersHTML += '<div class="col-xxl-12" style="">' #CONTENEDOR EXTERNO
            workOrdersHTML += '<div class="card card-xxl-stretch mb-8 mb-xl-12 ps-3">' #BORDE ITEM style="border:1px solid white; border-width:1px;"

            #Tiulo colapsable
            title = '<span class="card-label fw-bolder fs-3 me-4">Work Order: ' + str(woN) + '</span>  ' + getStateName(wo.state.id, 'WO')
            workOrdersHTML += htmlDivCollapse("divWO", str(wo.id), title, 2)            

            #Titulo
            workOrdersHTML += '<div class="card-header border-0">'         

                        
            workOrdersHTML += '<div class="col-lg-12">'
          
            
            workOrdersHTML += '<div class="row pb-2">'
            
            #Celda 1
            workOrdersHTML += '<div class="col-lg-4">' #style="border:1px solid red; border-width:1px;"
            
            workOrdersHTML += '<h3 class="card-title align-items-start flex-column">'            
            
            #Subtitulo
            workOrdersHTML += ''
            workOrdersHTML += '<span class="text-muted mt-1 fw-bold fs-7">' + stateDescription + '</span>'
            workOrdersHTML += '</h3>'

            if wo.state.id == 1 and mode == 1: #Solo si se edita

                workOrdersHTML += '<div class="col-lg-4"><a id="aAddItem" class="btn btn-light-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalItem" onclick="wo(' + str(wo.id) + ')"><span class="svg-icon svg-icon-12"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M8 1a.5.5 0 0 1 .5.5V7h5.5a.5.5 0 0 1 0 1H8.5v5.5a.5.5 0 0 1-1 0V8H2a.5.5 0 0 1 0-1h5.5V1.5A.5.5 0 0 1 8 1z"/></svg></span><b>Add Item</b></a></div>'
                
            workOrdersHTML += '</div>'


            #Celda 2
            workOrdersHTML += '<div class="col-lg-2">' #style="border:1px solid green; border-width:1px;"            

            if wo.state.id >= 5:
                
                if mode == 1:                    
                    # workOrdersHTML += '<a href="../../generate_pdf/' + str(wo.id) + '" class="fs-6 text-hover-primary" target="_blank">Download WO</a>'
                    workOrdersHTML += '<img alt="" class="w-20px me-2" src="/static/images/pdf.svg" alt=""><a id="downloadWO" class="btn btn-light-danger btn-sm" data-bs-toggle="modal" data-bs-target="#modalWO" onclick="loadModalWO(' + str(wo.id) + ')"><b>View WO</b></a>'

                else:
                    workOrdersHTML += '<img alt="" class="w-20px me-2" src="/static/images/pdf.svg" alt=""><a href="../../proyect/generate_pdf/' + str(wo.id) + '" class="btn btn-light-danger btn-sm" target="_blank"><b>View WO</b></a>'



            workOrdersHTML += '</div>'


            #Celda 3
            workOrdersHTML += '<div class="col-lg-2">' #style="border:1px solid green; border-width:1px;"            

            if mode == 1:
                workOrdersHTML += '<a id="aAddItem" class="btn btn-light-info btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,1)"><span class="svg-icon" style="width:12px; height:12px; display:inline-block;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/><line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/></svg></span><b>Schedule</b></a>'

            workOrdersHTML += '</div>'


            #Celda 4
            workOrdersHTML += '<div class="col-lg-2">' #style="border:1px solid green; border-width:1px;"

            if mode == 1:
                if mode == 1 and len(items) > 0: # Solo si se edita

                    if wo.state.id == 2:                        
                        workOrdersHTML += '<a class="btn btn-light-success btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)"><span class="svg-icon svg-icon-12"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M21 6v9a3 3 0 0 1-3 3H8l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><b>Add general quote</b></a>'


                    if wo.state.id == 3:                        
                        workOrdersHTML += '<a class="btn btn-light-success btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)"><span class="svg-icon svg-icon-12"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M21 6v9a3 3 0 0 1-3 3H8l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><b>Add general approve quote</b></a>'                        

                    if wo.state.id >= 4 and wo.state.id <= 10:                        
                        workOrdersHTML += '<a class="btn btn-light-success btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)"><span class="svg-icon svg-icon-12"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M21 6v9a3 3 0 0 1-3 3H8l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><b>Add general comment</b></a>'                        
                

            workOrdersHTML += '</div>'

          

            #Celda 5
            workOrdersHTML += '<div class="col-lg-2 text-end">' #style="border:1px solid yellow; border-width:1px;"
            
            if wo.state.id < 10 and mode == 1: #Solo si se edita

                 workOrdersHTML += '<a id="aState" href="javascript:state(' + str(wo.id) + ',' + str(wo.state.id) + ')" class="btn btn-sm btn-primary font-weight-bolder text-uppercase" data-bs-toggle="tooltip" title="' + buttonDescription + '">' + buttonName + '</a>'
                 workOrdersHTML += '<input id="stateAfter" type="hidden" value="' + stateNewName + '">'
                                    
            workOrdersHTML += '</div>'

            workOrdersHTML += '</div>'
                    

            workOrdersHTML += '</div></div>'
            #Fin Titulo


            

            #Lista de Items
                                                   
            #Detalle de los items
            workOrdersHTML += '<div id="itemsDetails_' + str(wo.id) + '">'
            workOrdersHTML += getDataItems(request, wo.id, mode)
            workOrdersHTML += '</div>'

            #Comentarios genéricos por etapa/estado
            workOrdersHTML += getDataComments(request, wo.id, 0, mode)
                        
            
           

            #Fin colapsable            
            workOrdersHTML += '</div></div>'

            workOrdersHTML += '</div>' #Fin BORDE ITEM            
            workOrdersHTML += '</div>' #FIN CONTENEDOR EXTERNO            
            workOrdersHTML += '</div>' #FIN WO

            

    
    

    # if (len(items) > 0 and mode == 1) or (len(workOrders) == 0 and mode == 1): # Solo si se edita:
    
    #     workOrdersHTML += '<div class="d-flex justify-content-star flex-shrink-0">'
    #     workOrdersHTML += '<a class="btn btn-link fs-6" onclick="addWO(' + str(proyect_id) + ')">Add Work Order (+)</a>'
    #     workOrdersHTML += '</div>'

    return workOrdersHTML


#Consulta realizada mientras se consultan las WO´s. Aquí se obtiene el detalle.
def getDataItems(request, workOrderId, mode): # mode 1: edicion, 2: lectura
    																									    
    itemsHTML = ""

    try:

        workOrder = WorkOrder.objects.get(id=workOrderId)
        items = Item.objects.filter(workorder = workOrder).order_by('id')
        itemN = 0
        codeWO = workOrder.proyect.code
        
        for item in items:

            fecha_propuesta = ''            
            code = ''
            group = ''
            itemN+= 1

            if codeWO:
                code = codeWO + '-' + str(itemN)

            if not item.code or item.code != code:
                item.code = code
                item.save()

            if item.status == 1: # Mostrar solo si está activo


                if item.group:
                    group = item.group.name

                try:
                    if item.date_proposed:
                        fecha_propuesta = timezone.localtime(item.date_proposed).strftime('%m/%d/%Y')                

                    if not workOrder.proyect.code:
                        code = str(itemN)                    
                
                except ValueError:
                    messages.error('Server error. Date not exist!')
                

                itemsHTML += '<div class="row itemCount_' + str(workOrderId) + ' mb-10" style="border: 1px solid #d7d9dc; border-radius: .475rem">' #fila item
                
                itemsHTML += '<div class="col-lg-12">'  #contenedor generico style="border:3px solid white; border-width:1px;"

                #Inicio Fila 1
                
                itemsHTML += '<div class="row p-2">'

                #Codigo item
                itemsHTML += '<div class="col-xl-6 align-items-start">' # style="border:1px solid white; border-width:1px;"

                itemsHTML += '<div class="fs-6 fw-bold mt-3">'
                itemsHTML += '<b>' + code  + '</b>'
                itemsHTML += '</div>'

                itemsHTML += '</div>'
                              
                
                itemsHTML += '<div class="col-xl-2">' # style="border:1px solid white; border-width:1px;"

                if mode == 1: #edicion

                    if workOrder.state.id == 5:
                        itemsHTML += '<a class="btn btn-light-info btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,1)"><span class="svg-icon" style="width:12px; height:12px; display:inline-block;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/><line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/></svg></span><b>Due date</b></a>'

                itemsHTML += '</div>'




                # #Acciones (comentarios)
                itemsHTML += '<div class="col-xl-2">' # style="border:1px solid white; border-width:1px;"

                if mode == 1: #edicion

                    if workOrder.state.id >= 2:
                        itemsHTML += '<a class="btn btn-light-success btn-sm" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)"><span class="svg-icon svg-icon-12"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M21 6v9a3 3 0 0 1-3 3H8l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span><b>' + workOrder.state.linkDescription + '</b></a>'

                    # if workOrder.state.id == 3:
                    #     itemsHTML += '<a class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)">Approve quote (+)</a>'

                    # if workOrder.state.id >= 4:
                    #     itemsHTML += '<a class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)">Add comment (+)</a>'
                    
                itemsHTML += '</div>'



                
                itemsHTML += '<div class="col-xl-2 text-end">' # style="border:1px solid white; border-width:1px;"

                if mode == 1: #edicion

                    # #Acciones (editar, eliminar)
                    if workOrder.state.id in (1,2,3,4,5,6,7,8,9):

                        itemsHTML += '<a href="#" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm me-1" onclick="editItem(' + str(workOrderId) + ',' + str(item.id) + ')"><span class="svg-icon svg-icon-3" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M21.4 8.35303L19.241 10.511L13.485 4.755L15.643 2.59595C16.0248 2.21423 16.5426 1.99988 17.0825 1.99988C17.6224 1.99988 18.1402 2.21423 18.522 2.59595L21.4 5.474C21.7817 5.85581 21.9962 6.37355 21.9962 6.91345C21.9962 7.45335 21.7817 7.97122 21.4 8.35303ZM3.68699 21.932L9.88699 19.865L4.13099 14.109L2.06399 20.309C1.98815 20.5354 1.97703 20.7787 2.03189 21.0111C2.08674 21.2436 2.2054 21.4561 2.37449 21.6248C2.54359 21.7934 2.75641 21.9115 2.989 21.9658C3.22158 22.0201 3.4647 22.0084 3.69099 21.932H3.68699Z" fill="black" /><path d="M5.574 21.3L3.692 21.928C3.46591 22.0032 3.22334 22.0141 2.99144 21.9594C2.75954 21.9046 2.54744 21.7864 2.3789 21.6179C2.21036 21.4495 2.09202 21.2375 2.03711 21.0056C1.9822 20.7737 1.99289 20.5312 2.06799 20.3051L2.696 18.422L5.574 21.3ZM4.13499 14.105L9.891 19.861L19.245 10.507L13.489 4.75098L4.13499 14.105Z" fill="black" /></svg></span></a>'
                        itemsHTML += '<a href="#" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm" onclick="delI(this,' + str(item.id) + ')"><span class="svg-icon svg-icon-3" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" /><path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" /><path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" /></svg></span></a>'
                    

                itemsHTML += '</div>'

                #Fin fila 1
                itemsHTML += '</div>'


                # Linea azul
                itemsHTML += '<div class="h-3px w-100 bg-primary col-lg-4"></div><br/>'

                                                
                
                # Inicio fila 2
                itemsHTML += '<div class="col-lg-12">' #style="border:1px solid white; border-width:1px;"
                                
                itemsHTML += '<div class="row">'
                                
                ##############################################################################################################
                ############################################## Celda (cabecera) ##############################################
                ##############################################################################################################

                place = ''
                if item.place:
                    place = item.place.name


                itemsHTML += '<div class="col-xl-4">' # style="border:1px solid white; border-width:1px;"
                itemsHTML += '<table><tbody>'
                itemsHTML += '<tr><td><b>Category:</b> ' + item.subcategory.category.name + '</td></tr>'
                itemsHTML += '<tr><td><b>Sub Category:</b> ' + item.subcategory.name + '</td></tr>'
                itemsHTML += '<tr><td><b>Group:</b> ' + group + '</td></tr>'
                itemsHTML += '<tr><td><b>Place:</b> ' + place + '</td></tr>'
                itemsHTML += '<tr><td><b>QTY:</b> ' + item.qty + '</td></tr>'
                itemsHTML += '<tr><td><b>Proposed date:</b> ' + fecha_propuesta + '</td></tr>'
                itemsHTML += '<tr><td><b>Notes:</b> ' + item.notes + '</td></tr>'
                
                if workOrder.state.id >= 5:

                    responsibleName = ''
                    dueDate = ''

                    calendar = CalendarItem.objects.filter(item = item).first()

                    if calendar:

                        if calendar.responsible:
                            responsibleName = calendar.responsible.name

                        if calendar.date_start:
                            if calendar.allday:
                                dueDate = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y')
                            else:
                                dueDate = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %I:%M %p')

                    itemsHTML += '<tr><td><b>Responsible:</b> ' + responsibleName + '</td></tr>'
                    itemsHTML += '<tr><td><b>Due date:</b> ' + dueDate + '</td></tr>'


                itemsHTML += '</tbody></table>'
                itemsHTML += '</div>'
                

                ##############################################################################################################
                ############################################# Celda (atributos) ##############################################
                ##############################################################################################################

                itemsHTML += '<div class="col-xl-3">' # style="border:1px solid white; border-width:1px;"
                itemsHTML += '<table><tbody>'

                attributes = ItemAttribute.objects.filter(item = Item.objects.get(id=item.id))
                for attribute in attributes:
                    
                    if attribute.attribute.multiple:                    
                        itemsHTML += '<tr><td><b>' + attribute.attribute.name + ':</b> '

                        attributenotes = ItemAttributeNote.objects.filter(itemattribute = attribute)
                        for note in attributenotes:
                            # itemsHTML += note.attributeoption.name + ' <i class="fas fa-question-circle" data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<img src=\'' + note.attributeoption.file.url + '\' style=\'width: 100px; height: 100px;\'"></i>, '
                            
                            if note.attributeoption.file:
                                itemsHTML += note.attributeoption.name + ' <i class="fas fa-question-circle" data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="&lt;img src=\'' + note.attributeoption.file.url + '\' width=\'200\' >"></i>, '
                            else:
                                itemsHTML += note.attributeoption.name + ', '
                            #itemsHTML = f"{note.attributeoption.name} <i class='fas fa-question-circle' data-bs-toggle='tooltip' data-bs-html='true' data-bs-title='<img src=\"{note.attributeoption.file.url}\" style=\"width: 50px; height: 50px; object-fit: cover;\">'></i>, "

                        itemsHTML = itemsHTML[:-2]
                        
                        itemsHTML += '</td></tr>'

                    else:
                        itemsHTML += '<tr><td><b>' + attribute.attribute.name + ':</b> ' + attribute.notes + '</td></tr>'

                itemsHTML += '</tbody></table>'
                itemsHTML += '</div>'       
                

                ##############################################################################################################
                ############################################ Celda (materiales) ##############################################
                ##############################################################################################################
                
                itemsHTML += '<div class="col-xl-5">' #style="border:1px solid white; border-width:1px;"
                itemsHTML += '<h6>Materials:</h6>'
                itemsHTML += '<form method="POST" class="formMaterial"><div class="table-responsive">'
                itemsHTML += '<table class="table table-striped" width="100%"><tbody>'
                            
                materials = ItemMaterial.objects.filter(item = item).order_by('notes')        # Notes es el nombre del archivo.             

                icon = '<span class="svg-icon svg-icon-primary svg-icon-1x"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24px" height="24px" viewBox="0 0 24 24" version="1.1">'
                icon += '<defs/>'
                icon += '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">'
                icon += '<rect x="0" y="0" width="24" height="24"/>'
                icon += '<path d="M15.9497475,3.80761184 L13.0246125,6.73274681 C12.2435639,7.51379539 12.2435639,8.78012535 13.0246125,9.56117394 L14.4388261,10.9753875 C15.2198746,11.7564361 16.4862046,11.7564361 17.2672532,10.9753875 L20.1923882,8.05025253 C20.7341101,10.0447871 20.2295941,12.2556873 18.674559,13.8107223 C16.8453326,15.6399488 14.1085592,16.0155296 11.8839934,14.9444337 L6.75735931,20.0710678 C5.97631073,20.8521164 4.70998077,20.8521164 3.92893219,20.0710678 C3.1478836,19.2900192 3.1478836,18.0236893 3.92893219,17.2426407 L9.05556629,12.1160066 C7.98447038,9.89144078 8.36005124,7.15466739 10.1892777,5.32544095 C11.7443127,3.77040588 13.9552129,3.26588995 15.9497475,3.80761184 Z" fill="#000000"/>'
                icon += '<path d="M16.6568542,5.92893219 L18.0710678,7.34314575 C18.4615921,7.73367004 18.4615921,8.36683502 18.0710678,8.75735931 L16.6913928,10.1370344 C16.3008685,10.5275587 15.6677035,10.5275587 15.2771792,10.1370344 L13.8629656,8.7228208 C13.4724413,8.33229651 13.4724413,7.69913153 13.8629656,7.30860724 L15.2426407,5.92893219 C15.633165,5.5384079 16.26633,5.5384079 16.6568542,5.92893219 Z" fill="#000000" opacity="0.3"/>'
                icon += '</g>'
                icon += '</svg></span>'

                if len(materials) > 0:

                    if workOrder.state.id >= 1: #Antes estaba desde el estado 4. Ahora, desde el 1.
                        itemsHTML += '<thead><tr><th style="min-width:150px"></th><th>QTY</th><th>Received QTY</th><th>Received Date</th></thead>'
                    else:
                        itemsHTML += '<thead><tr><th style="max-width:50px"></th><th style="max-width:50px">QTY</th><th></th><th></th></thead>'

                    for material in materials:

                        materialName = str(material.notes)
                        qty = str(material.qty)   
                        qtyR = ''             
                        dateR = ''
                        materialId = str(material.id)

                        background = "background-color: #ffffff"

                        # if qty != '' and (workOrder.state.id < 4):
                        #     materialName += ' / ' + qty

                        if material.qty_received:
                            qtyR = material.qty_received

                        if material.date_received:
                            dateR = material.date_received
                        
                        itemsHTML += '<tr><td valign="middle" style="padding:0px;">' + icon + ' ' + materialName + '</td>'                

                        # if workOrder.state.id < 4:
                        #     itemsHTML += '<td style="padding:2px;">' + str(qty) + '</td>'

                        # if workOrder.state.id <= 5 and mode == 1: #edicion
                        if mode == 1: #edicion

                            itemsHTML += '<td style="padding:0px"><input type="text" class="form-control mb-1" value="' + str(qty) + '" readonly style="background: none"/></td>'
                            itemsHTML += '<td style="padding:0px"><input type="text" class="form-control mb-1" name="qtyR_' + materialId + '" value="' + str(qtyR) + '" maxlength="100"/></td>'
                            itemsHTML += '<td style="padding:0px"><input class="form-control receivedDate" name="dateR_' + materialId + '" placeholder="Pick a date" style="width: 100px" value="' + dateR + '"/></td>'

                        # elif workOrder.state.id >= 6 or mode == 2: #solo lectura
                        elif mode == 2: #solo lectura

                            # if mode == 2:
                            #     color = "#ffffff"

                            itemsHTML += '<td style="padding:2px">' + str(qty) + '</td>'
                            itemsHTML += '<td style="padding:2px">' + str(qtyR) + '</td>'
                            itemsHTML += '<td style="padding:2px">' + dateR + '</td>'
                            

                        itemsHTML += '</tr>'

                    # if workOrder.state.id <= 5 and mode == 1: #edicion
                    if mode == 1: #edicion
                        itemsHTML += '<tr><td colspan=3></td></tr>'
                        itemsHTML += '<tr><td colspan=3 align="right" class="bg-white"><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></td></tr>'

                itemsHTML += '</tbody></table></div></form>'    

                itemsHTML += '</div>'


                ## Fin Fila 2 ##
                itemsHTML += '</div>'                                        
                
                itemsHTML += '</div>'



                ##############################################################################################################
                ############################################## Comentarios Items #############################################
                ##############################################################################################################

                
                itemsHTML += getDataComments(request, workOrder.id, item.id, mode)

                # #Aprobar cotizacion
                # if workOrder.state.id == 3:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Do you approve the quote?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtQuote_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + str(quote) + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'


                # #Aprobar instalación
                # if workOrder.state.id == 6:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Has the installation been completed?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtInstalling_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + '                 ' + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'


                # #Aprobación del cliente
                # if workOrder.state.id == 7:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Has the customer fully accepted the work?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtCustomer_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + '                 ' + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'


                # #Aprobación del cliente
                # if workOrder.state.id == 8:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Are there any additional items or changes that need to be included in the final invoice?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtCustomer_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + '                 ' + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'


                # #Últimos ajustes
                # if workOrder.state.id == 8:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Are there any additional items or changes that need to be included in the final invoice?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtCustomer_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + '                 ' + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'


                # #Últimos ajustes
                # if workOrder.state.id == 9:

                #     itemsHTML += '<div class="col-lg-11 fv-row text-start">'
                #     itemsHTML += '<div class="card rounded border-success border border-dashed p-1">'
                #     itemsHTML += '<div class="card-body my-1">'                

                #     itemsHTML += '<form method="POST" class="formQuote">'
                    
                #     itemsHTML += '<h6>Has the final payment been received from the customer?</h6>'

                #     quote = ''
                #     id = str(item.id)

                #     if item.quote:
                #         quote = item.quote

                #     # itemsHTML += '<div class="form-switch form-check-custom form-check-solid me-1">'
                #     #itemsHTML += '<input class="form-check-input approve" type="checkbox">'
                    
                #     # checked = ''
                    
                #     # if int(item.status) == 2:
                #     #     checked = 'checked="checked"'
                    
                #     # itemsHTML += '<input class="form-check-input approve" type="checkbox" value="1" ' + checked + ' style="height: 1.75rem;" onchange="app(this,' + str(item.id) + ')">'                                                
                #     # itemsHTML += '<span class="form-check-label fw-bold text-muted">  Yes</span>'
                #     # itemsHTML += '</div>'

                #     itemsHTML += '<br/><textarea name="txtCustomer_' + id + '" class="form-control form-control-solid h-80px" maxlength="2000">' + '                 ' + '</textarea>'
                #     itemsHTML += '<div class="text-end"><br/><button type="submit" class="btn btn-primary px-6 py-1 mr-4" data-kt-indicator="off"><span class="indicator-label">Save</span></button></div>'

                #     itemsHTML += '</form>'

                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                #     itemsHTML += '</div>'
                

                ##############################################################################################################
                ########################################## Más detalles (archivos) ###########################################
                ##############################################################################################################
                
                files = ItemFile.objects.filter(item = item)
                materials = ItemMaterial.objects.filter(item = item, file__isnull = False).exclude(file='').order_by('name')
                images = ItemImage.objects.filter(item = item)

                if len(files) > 0 or len(materials) > 0 or len(images) > 0:

                    # itemsHTML += '<div class="separator border-secondary my-10"></div>'

                    #Inicio Fila 4
                    #Ver detalle

                    itemsHTML += htmlDivCollapse("divItemDetail", str(item.id), 'See more details', 1)  #mode1: colapsado mode2: open


                    ##############################################################################################################
                    ############################################## Celda (archivos) ##############################################
                    ##############################################################################################################
                  

                    if len(files) > 0 or len(materials) > 0:

                        itemsHTML += '<div class="col-lg-12">' # style="border:1px solid white; border-width:1px;"
                        itemsHTML += '<div class="row">'
                        itemsHTML += '<div class="col-xl-12">'

                        itemsHTML += '<div class="d-flex align-items-center border p-5">'
                        itemsHTML += '<ul class="text-start">'

                        for file in files:

                            itemsHTML += '<li>'
                                                
                            if file.file.url[-4:] == '.pdf':
                                itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/pdf.svg" alt="">'

                            if file.file.url[-5:] == '.docx' or file.file.url[-4:] == '.doc':
                                itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/doc.svg" alt="">'

                            if file.file.url[-5:] == '.xlsx' or file.file.url[-4:] == '.xls':
                                itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/xls.svg" alt="">'

                            if file.file.url[-5:] == '.pptx' or file.file.url[-4:] == '.ppt':
                                itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/ppt.svg" alt="">'
                                                            
                            itemsHTML += '<span>'
                            itemsHTML += '<a href="' + file.file.url + '" class="fs-7 text-hover-primary" target="_blank">' + file.name + '</a>'
                            itemsHTML += '<div class="text-gray-400">' + file.notes + '</div>'
                            itemsHTML += '</<span>' 

                            itemsHTML += '</li>'

                        for material in materials:

                            try:
                            
                                if material.file:

                                    if material.file.url[-4:] in ('.pdf','.doc','.xls') or material.file.url[-5:] in ('.docx','.xlsx'):

                                        itemsHTML += '<li>'
                                                            
                                        if material.file.url[-4:] == '.pdf':
                                            itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/pdf.svg" alt="">'

                                        if material.file.url[-5:] == '.docx' or material.file.url[-4:] == '.doc':
                                            itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/doc.svg" alt="">'

                                        if material.file.url[-5:] == '.xlsx' or material.file.url[-4:] == '.xls':
                                            itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/xls.svg" alt="">'

                                        if material.file.url[-5:] == '.pptx' or material.file.url[-4:] == '.ppt':
                                            itemsHTML += '<img alt="" class="w-30px me-3" src="/static/images/ppt.svg" alt="">'
                                                                        
                                        itemsHTML += '<span>'
                                        itemsHTML += '<a href="' + material.file.url + '" class="fs-7 text-hover-primary" target="_blank">' + material.name + '</a>'
                                        itemsHTML += '<div class="text-gray-400">' + material.notes + '</div>'
                                        itemsHTML += '</<span>' 

                                        itemsHTML += '</li>'
                            
                            except:
                                pass
                            

                        itemsHTML += '</ul>'
                        itemsHTML += '</div>'         
                                                                                                                                                    
                        itemsHTML += '</div>'
                        itemsHTML += '</div>'
                        itemsHTML += '</div>'
                    #############

                    itemsHTML += '</div>'


                    itemsHTML += '<div class="row">' # style="border:1px solid white; border-width:1px;"

                    ##############################################################################################################
                    ############################################## Celda (imagenes) ##############################################
                    ##############################################################################################################

                    itemsHTML += '<div class="col-lg-12">' # style="border:1px solid white; border-width:1px;"
                    itemsHTML += '<section class="grid-gallery-section">'
                    
                    # itemsHTML += '<div id="gallery-filters" class="gallery-button-group">'
                    # itemsHTML += '<button class="filter-button is-checked showImg" data-filter="*">ALL FILES</button>'
                    # itemsHTML += '<button class="filter-button" data-filter=".Image">IMAGES</button>'
                    # itemsHTML += '<button class="filter-button" data-filter=".Material">MATERIAL</button>'
                    # itemsHTML += '</div>'
                    
                    itemsHTML += '<div class="grid-gallery">'
                    itemsHTML += '<div class="gallery-grid-sizer"></div>'            		

                    
                    for image in images:

                        type_imp = 'Image'

                        if image.file:
                                            
                            itemsHTML += '<div class="gallery-grid-item ' + type_imp + '">'
                            itemsHTML += '<div class="gallery-image-area" style="width:80%">'
                            
                            itemsHTML += '<img src="' + image.file.url + '" class="grid-thumbnail-image" alt="' + image.name + '"><br/>"' + image.notes + '"'
                            itemsHTML += '<div class="gallery-overly">'
                            
                            itemsHTML += '<div class="image-details">'                                
                            itemsHTML += '<span class="image-title">' + type_imp + '</span>'                                
                            itemsHTML += '</div>'
                            
                            itemsHTML += '<a class="grid-image-zoom" href="' + image.file.url + '" data-fancybox-group="grid-gallery" title="' + image.notes + '">	'
                            itemsHTML += '<div class="gallery-zoom-icon"></div>'
                            itemsHTML += '</a>'

                            itemsHTML += '</div>'
                            itemsHTML += '</div>'
                            itemsHTML += '</div>'


                    for material in materials:

                        type_imp = 'Material'
                            
                        if material.file:
                            try:
                                if material.file.url[-4:] not in ('.pdf','.doc','.xls') and material.file.url[-5:] not in ('.docx','.xlsx'):

                                    itemsHTML += '<div class="gallery-grid-item ' + type_imp + '">'
                                    itemsHTML += '<div class="gallery-image-area" style="width:80%">'

                                    itemsHTML += '<img src="' + material.file.url + '" class="grid-thumbnail-image" alt="' + material.name + '"><br/>"' + material.notes + '"'
                                    itemsHTML += '<div class="gallery-overly">'

                                    itemsHTML += '<div class="image-details">'
                                    itemsHTML += '<span class="image-title">' + type_imp + '</span>'
                                    itemsHTML += '</div>'

                                    itemsHTML += '<a class="grid-image-zoom" href="' + material.file.url + '" data-fancybox-group="grid-gallery" title="' + material.notes + '">'
                                    itemsHTML += '<div class="gallery-zoom-icon"></div>'
                                    itemsHTML += '</a>'

                                    itemsHTML += '</div>'
                                    itemsHTML += '</div>'
                                    itemsHTML += '</div>' 

                            except:
                                pass
                                

                    itemsHTML += '</div>'
                    itemsHTML += '</section>'
                    
                    itemsHTML += '</div>'                                    
                    #############            
                    
                    itemsHTML += '</div>' 

                    itemsHTML += '</div>' #div Detalle    


                                        
                itemsHTML += '</div>'  # Final Final contenedor generico      
                itemsHTML += '</div>'  # Final row item
        


    except ValueError:
        messages.error('Server error. Please contact to administrator!')
        
    return itemsHTML


#Consulta realizada para obtener los datos de cada uno de los comentarios.
def getDataComments(request, workOrderId, itemId, mode): # mode 1: edicion, 2: lectura
    
    workorder = WorkOrder.objects.get(id=workOrderId)    
    itemsHTML = ''
    itemTxt = ''

    itemCSs = None #Comentario texto
    itemCSF = None #Comentario archivos

    stateName = ""

    if int(itemId) != 0:        
        item = Item.objects.get(workorder=workorder, id=itemId)

        if item:
            itemCSs = ItemCommentState.objects.filter(item=item).order_by('-id')  

            if len(itemCSs) > 0:
                itemsHTML += '<div class="separator border-secondary my-10"></div>'
                itemsHTML += htmlDivCollapse("divCommentItem", str(itemId), "Comments by item:", 2)

    else:         
        itemCSs = WorkOrderCommentState.objects.filter(workorder=workorder).order_by('-id')

        if len(itemCSs) > 0:            
            itemsHTML += htmlDivCollapse("divGeneralCommentItem", str(workOrderId), "General comments by item:", 2)            

    
    if len(itemCSs) > 0:
        itemsHTML += '<div class="col-xl-12 fv-row text-start"><div class="table-responsive">'
        # 27-04-2025
        itemsHTML += '<table class="table table-rounded table-striped"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="15%">State</th><th width="10%">Date</th><th width="10%">Time</th><th width="10%">User</th><th width="5%">Accepted</th><th>Notes</th>'

        if mode == 1:
            itemsHTML += '<th></th>'

        itemsHTML += '</tr></thead>'


    for itemCS in itemCSs:
        
        state = 'state_' #Clase usada por JS, para validar el avance entre los distintos estados
        date = ''
        time = ''
        stateName = ''
        username = ''
        itemTxt = ''

        if int(itemId) != 0:        
            itemCSF = ItemCommentStateFile.objects.filter(item_comment_state = itemCS).order_by('-id')
            state += str(itemCS.state.id)
        else:            
            itemCSF = WorkOrderCommentStateFile.objects.filter(workorder_comment_state = itemCS).order_by('-id')
            state += 'G_' + str(itemCS.state.id) + '_' + str(workorder.id)

        if itemCS.notes:
            itemTxt = itemCS.notes

        

        if itemCS.modification_date:
            date = timezone.localtime(itemCS.modification_date).strftime('%m/%d/%Y')
            time = timezone.localtime(itemCS.modification_date).strftime('%H:%M %p')

        if itemCS.state:
            stateName = getStateName(itemCS.state.id, 'TC')

        user = User.objects.get(id=itemCS.modification_by_user)

        if user:
            username = user.username

        if itemCSF:            
            itemTxt += '<ul class="text-start py-1">'
            
            for file in itemCSF:                    
                itemTxt += '<li><a href=' + file.file.url + ' target="_blank">' + file.name + '</a>'
            
            itemTxt += "</ul>"

        accepted = ''

        if itemCS.accepted:
            accepted = '<img src="/static/images/check2.svg" alt="Logo" width="15">'

        itemsHTML += '<tr class="py-0 fw-bold fs-7 ' + state + '"><td style="padding:0; border:0">' + stateName + '</td><td>' + date + '</td><td>' + time + '</td><td>' + username + '</td><td align=center>' + accepted +'</td><td>' + itemTxt + '</td>'

        user_session = request.user

        if user == user_session and workorder.state == itemCS.state and mode == 1: #edicion
            itemsHTML += '<td><a class="py-0 btn btn-link fs-7" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrderId) + ',' + str(itemId) + ',' + str(itemCS.id) + ',0)">Edit</a></td>'
        else:
             itemsHTML += '<td></td>'
        itemsHTML += '</tr>'
        

    #Se cierra panel colapsable

    if len(itemCSs) > 0:
        itemsHTML += '</table></div></div>'
        itemsHTML += '</div></div>'

    return itemsHTML


#Consulta realizar al crear un proyecto, para obtener todos los proyectos de tal cliente
def getCustomer(filtersCustomer, caso):

    customer_data = []

    if filtersCustomer is None:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(filtersCustomer)

    # Creamos una lista con los datos de cada proyecto
    for customer in customers:      
        
        proyects = Proyect.objects.filter(customer = customer)
        proyectId = ''

        for proyect in proyects:
            proyectId = str(proyect.id)

        if (caso == 1 and proyectId != '') or caso == 2:

            customer_data.append({
                'id': customer.id,
                'customerName': customer.name,
                'address': customer.address,
                'city': customer.city,
                'state_u': customer.state,
                'zipcode': customer.zipcode,
                'apartment': customer.apartment,                        
                'email': customer.email,
                'phone': customer.phone,
                'customerDescription': customer.description,
                'customerNotes': customer.notes,
                'id_proyect': proyectId,
            })
    
    return customer_data


##################################
## Funciones para ver modales ###
##################################

#Modal desarrollado para todo tipo de comentarios, ya sea generales o particulares.
def modalComment(workOrderId, itemId, commentId):
    
    workorder = WorkOrder.objects.get(id=workOrderId)            
    itemsHTML = ''    
    itemTxt = ''    
    fecha_fin = ''

    modalSubTitle = workorder.state.modalSubTitle

    item = None    
    files = None
    accepted = None

    itemCSId = "0"
    
    #Por item
    if int(itemId) != 0:
            
        item = Item.objects.get(workorder=workorder, id=itemId)

        if item:
            
            itemId = str(item.id)
            itemCS = ItemCommentState.objects.filter(id=commentId, item=item).first() 
                        
            if itemCS:
                itemCSId = str(itemCS.id)
                itemTxt = itemCS.notes
                accepted = itemCS.accepted
                files = ItemCommentStateFile.objects.filter(item_comment_state = itemCS)

    #General
    else:

        itemCS = WorkOrderCommentState.objects.filter(id=commentId, workorder=workorder).first() 

        if itemCS:
            itemCSId = str(itemCS.id)
            itemTxt = itemCS.notes
            accepted = itemCS.accepted
            files = WorkOrderCommentStateFile.objects.filter(workorder_comment_state = itemCS)
                
            
    #itemsHTML += '<div class="d-flex justify-content-start flex-shrink-0">'

    # itemsHTML += '<div class="modal-header">'
    # itemsHTML += '<h2>Title</h2>'
    # itemsHTML += '<div class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="modal">'
    # itemsHTML += '<span class="svg-icon svg-icon-1">'
    # itemsHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    # itemsHTML += '<rect opacity="0.5" x="6" y="17.3137" width="16" height="2" rx="1" transform="rotate(-45 6 17.3137)" fill="black" />'
    # itemsHTML += '<rect x="7.41422" y="6" width="16" height="2" rx="1" transform="rotate(45 7.41422 6)" fill="black" />'
    # itemsHTML += '</svg>'
    # itemsHTML += '</span>'
    # itemsHTML += '</div>'
    # itemsHTML += '</div>'
    
    itemsHTML += '<div class="col-xl-12 fv-row text-start">'      
    itemsHTML += '<form id="formItem_' + itemId + '" method="POST" enctype="multipart/form-data">'
    
    
    itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3">' + modalSubTitle + '</div> '
    
    if workorder.state.checkBoxDescription:
        if workorder.state.checkBoxDescription != '':            
            checked = ''
            if accepted:
                checked = 'checked'

            itemsHTML +='<div class="form-check pb-2"><input class="form-check-input" type="checkbox" name="chkState" ' + checked + '><label class="form-check-label">' + workorder.state.checkBoxDescription + '</label></div>'

    itemsHTML += '<textarea name="notes" class="form-control form-control-solid h-80px" maxlength="2000">' + str(itemTxt) + '</textarea><br/>'
        
    if files:        
        itemsHTML += '<ul class="text-start">'        
        for file in files:
            itemsHTML += '<li><a href=' + file.file.url + ' target="_blank">' + file.name + '</a>  <a href="" onClick="delFile(this, ' + str(file.id) + ', ' + itemCSId + ', ' + itemId + ', ' + str(workorder.id) + ',event)"<i class="fa fa-trash"></i></a>'
        itemsHTML += "</ul>"
                
    itemsHTML += '<input type="file" name="files" class="form-control form-control" multiple><br/>'
    
    itemsHTML += '<div class="row text-end">'

    itemsHTML += '<div class="col-md-12">'
    itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveComm(' + str(workorder.id) + ',' + itemId + ',' + commentId + ')">Save</button>'                
    itemsHTML += '</div>'    
        
    itemsHTML += '<div class="col-md-9">'                                    
    itemsHTML += '<div class="divItemMsg alert alert-warning text-start p-2 mb-1" style="display:none">Please, enter a comment.</div>'                
    itemsHTML += '</div>'                                
                                
    itemsHTML += '</div>'

    # Borrar archivos
    if itemCS:
        itemsHTML += '<script>$("#modalCommentDelete").show(); $("#modalCommentDelete").click(function() { delComm(' + itemCSId + ', ' + itemId + ', ' + str(workorder.id) + ',event)});</script>'
    # else:
    #     itemsHTML += '<script>$("#modalCommentDelete").hide(); $("#divModalDialog").removeClass("mw-900px").addClass("mw-650px");</script>'

    
    itemsHTML += '</form>'
    itemsHTML += '</div>'
#    itemsHTML += '</div>'

    return itemsHTML


#Modal desarrollado para todo tipo de calendarizacion, ya sea por wo o por item.
def modalCalendar(request, workOrderId, itemId, id):
    
    workorder = WorkOrder.objects.filter(id=workOrderId).first()
    item = Item.objects.filter(id=itemId).first()
    itemsHTML = '<div class="col-xl-12 fv-row text-start"><br/>'

    responsibleId = 0
    fecha_inicio = ''
    fecha_fin = ''
    fechaDate_inicio = ''
    fechaDate_fin = ''    
    allDay = False
    status = 0
    
    #Por item
    if item:
            
        calendar = CalendarItem.objects.filter(item=item).first()
        
        if calendar:            
            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %H:%M')
                fechaDate_inicio = fecha_inicio[11:16]

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%m/%d/%Y %H:%M')
                fechaDate_fin = fecha_fin[11:16]

            if calendar.responsible:
                responsibleId = calendar.responsible.id        

            if calendar.status:
                status = calendar.status

            if calendar.allday:
                allDay = True

        itemsHTML += '<form id="formItem_' + itemId + '" method="POST" enctype="multipart/form-data">'


        itemsHTML += '<b style="margin-left:-10px">Item:</b>'
        itemsHTML += '<div class="row"><div class="table-responsive">'

        if allDay and workorder.state.id > 5:
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="25%">Responsible</th><th width="50%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th><th width="0%"></th></tr></thead><tbody>'
        else:
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="25%">Responsible</th><th width="50%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th><th width="0%"></th></tr></thead><tbody>'
        
        itemsHTML += '<tr><td valign="top">'
        itemsHTML += str(item.code)
        itemsHTML += '</td><td>'
        itemsHTML += '<select class="form-select form-select-sm form-select-solid selectResponsible" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="responsible">'
        itemsHTML += htmlResponsibleSelect(responsibleId)
        itemsHTML += '</select>'
        itemsHTML += '</td><td>'
        
        if not allDay and workorder.state.id > 5:
            itemsHTML += '<div class="table-responsive"><table><tr><td>'
        
            itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateA" name="dateA" placeholder="Start" value="' + fecha_inicio + '" style="max-width: 90px"/>'
            itemsHTML += '</td><td>'
            itemsHTML += getDateSelect(name='dateA2', id='dateA2', classAdd='hour-picker', selected = fechaDate_inicio, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
            itemsHTML += '</td><td>'
            itemsHTML += '-'        
            itemsHTML += '</td><td>'
            itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
            itemsHTML += '</td><td>'
            itemsHTML += getDateSelect(name='dateB2', id='dateB2', classAdd='hour-picker', selected = fecha_fin, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
            itemsHTML += '</td><td>'

            itemsHTML += '<tr><td class="p-3 text-start" colspan=5>'

            if allDay:
                itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem" checked>'
            else:
                itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem">'
            
            itemsHTML += '<label class="form-check-label text-gray-700 fw-bold px-3">  All day</label>'
            itemsHTML += '</td></tr></table></div>'

        else:        
            itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateA" name="dateA" placeholder="Pick a date" value="' + fecha_inicio + '" style="width: 90px"/> <input name="checkAllDay" type="hidden" value="1">'
            # itemsHTML += '</td><td>'
            # itemsHTML += '<input class="form-control form-control-solid date-picker py-2" name="date2" placeholder="Pick a date" value="" style="width: 150px"/>'
        
        
        
        
        itemsHTML += '</td><td>'
        itemsHTML += htmlStatusCalendar(status, fecha_fin, calendar, 'statusDate')        
        itemsHTML += '</td></tr>'

        itemsHTML += '</tbody></table></div>'

        itemsHTML += '<br/>'

        itemsHTML += htmlDivCommentCalendar()

        #itemsHTML += '<br/>'

        itemsHTML += htmlDataCommentCalendar(request, workorder, item, None, 1)

        

        itemsHTML += '<div class="row text-end">'

        itemsHTML += '<div class="col-md-12 p-5">'
        itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveCalendar(' + str(workorder.id) + ',' + itemId + ',0)">Save</button>'
        itemsHTML += '</div>'                            
        
        itemsHTML += '</div>'
        
        # itemsHTML += '<script>$("#modalCommentDelete").hide(); $("#divModalDialog").removeClass("mw-650px").addClass("mw-900px"); </script>'

        itemsHTML += '</form>'

    #Work order
    elif workorder:
        
        calendar = CalendarWorkOrder.objects.filter(workorder=workorder).first()        

        if calendar:
            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %H:%M')
                fechaDate_inicio = fecha_inicio[11:16]

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%m/%d/%Y %H:%M')
                fechaDate_fin = fecha_fin[11:16]

            if calendar.allday:
                allDay = True                

            if calendar.responsible:
                responsibleId = calendar.responsible.id

            if calendar.status:
                status = calendar.status

        itemsHTML += '<form id="formItem_0" method="POST" enctype="multipart/form-data">' # Aca el itemId = 0
    
        # Work order
        
        itemsHTML += '<b style="margin-left:-10px">Work Order:</b>'
        itemsHTML += '<div class="row"><div class="table-responsive">' 
                        
        itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="5%">N°</th><th width="30%">Responsible</th><th width="50%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'
        
        itemsHTML += '<tr><td valign="top">'
        itemsHTML += str(workorder.code)
        itemsHTML += '</td><td>'
        itemsHTML += '<select class="form-select form-select-sm form-select-solid selectResponsible" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="responsible">'
        itemsHTML += htmlResponsibleSelect(responsibleId)
        itemsHTML += '</select>'
        itemsHTML += '</td><td>'
        
        # Date Start - End
        
        itemsHTML += '<div class="table-responsive"><table><tr><td>'
        
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateA" name="dateA" placeholder="Start" value="' + fecha_inicio + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += getDateSelect(name='dateA2', id='dateA2', classAdd='hour-picker', selected = fechaDate_inicio, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '-'        
        itemsHTML += '</td><td>'
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += getDateSelect(name='dateB2', id='dateB2', classAdd='hour-picker', selected = fecha_fin, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'

        itemsHTML += '<tr><td class="p-3 text-start" colspan=5>'

        if allDay:
            itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem" checked>'
        else:
            itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem">'
        
        itemsHTML += '<label class="form-check-label text-gray-700 fw-bold px-3">  All day</label>'
        itemsHTML += '</td></tr></table></div>'
        
                        
        itemsHTML += '</td><td>'
        itemsHTML += htmlStatusCalendar(status, fecha_fin, calendar, 'statusDate')
        itemsHTML += '</td></tr>'

        itemsHTML += '</tbody></table></div>'

        itemsHTML += '</div>'

        itemsHTML += htmlDivCommentCalendar()

        itemsHTML += '<br/>'

        itemsHTML += htmlDataCommentCalendar(request, workorder, item, None, 1)
                
        itemsHTML += '<br/>'


        items = Item.objects.filter(workorder=workorder).order_by('id')

        if id == '0' and len(items) > 0 and workorder.state.id == 6: # Para filtrar en el calendario, solo en la etapa 6.
        
            # Items
            
            itemsHTML += '<b style="margin-left:-10px">Items:</b>'
            itemsHTML += '<div class="row"><div class="table-responsive">'                            
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="25%">Responsible</th><th width="50%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'

            itemN = 0
            for item in items:
                
                itemN+= 1
                responsibleId = 0
                fecha_inicio = ''
                fecha_fin = ''
                fechaDate_inicio = ''
                fechaDate_fin = ''
                status = 0
                allDay = False                
                
                if item.status == 1:

                    calItem = CalendarItem.objects.filter(item = item).first()

                    if calItem:
                        if calItem.date_start:
                            fecha_inicio = timezone.localtime(calItem.date_start).strftime('%m/%d/%Y %H:%M')
                            fechaDate_inicio = fecha_inicio[11:16]

                        if calItem.date_end:
                            fecha_fin = timezone.localtime(calItem.date_end).strftime('%m/%d/%Y %H:%M')
                            fechaDate_fin = fecha_fin[11:16]

                        if calItem.allday:
                            allDay = True                            

                        if calItem.responsible:
                            responsibleId = calItem.responsible.id

                        if calItem.status:
                            status = calItem.status

                    itemsHTML += '<tr><td valign="top">'
                    itemsHTML += workorder.proyect.code + '-' + str(itemN)
                    itemsHTML += '</td><td>'
                    itemsHTML += '<select class="form-select form-select-sm form-select-solid selectResponsible" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="responsible[]">'
                    itemsHTML += htmlResponsibleSelect(responsibleId)
                    itemsHTML += '</select>'
                    itemsHTML += '</td><td>'
                    
                    itemsHTML += '<div class="table-responsive"><table><tr><td>'
        
                    itemsHTML += '<input class="form-control form-control-solid date-picker py-2" name="dateItemA[]" placeholder="Start" value="' + fecha_inicio + '" style="max-width: 90px"/>'
                    itemsHTML += '</td><td>'
                    itemsHTML += getDateSelect(name='dateItemA2[]', id='dateItemA2[]', classAdd='hour-picker', selected = fechaDate_inicio, checked = allDay) # '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateItemA2[]" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
                    itemsHTML += '</td><td>'
                    itemsHTML += '-'        
                    itemsHTML += '</td><td>'
                    itemsHTML += '<input class="form-control form-control-solid date-picker py-2" name="dateItemB[]" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
                    itemsHTML += '</td><td>'
                    itemsHTML += getDateSelect(name='dateItemB2[]', id='dateItemB2[]', classAdd='hour-picker', selected = fechaDate_fin, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateItemB2[]" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
                    itemsHTML += '</td><td>'

                    itemsHTML += '<tr><td class="p-3 text-start" colspan=5>'

                    if allDay:
                        itemsHTML += '<input class="checkAllDayItem" type="hidden" name="checkAllDayItem[]" value="1"><input class="form-check-input checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem" checked>'
                    else:
                        itemsHTML += '<input class="checkAllDayItem" type="hidden" name="checkAllDayItem[]" value="0"><input class="form-check-input checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem">'
                    
                    itemsHTML += '<label class="form-check-label text-gray-700 fw-bold px-3">  All day</label>'
                    itemsHTML += '</td></tr></table></div>'
                    
                    itemsHTML += '</td><td>'
                    itemsHTML += htmlStatusCalendar(status, fecha_fin, calItem, 'statusDate[]')
                    itemsHTML += '<input type="hidden" name="id[]" value="' + str(item.id) + '" readonly/>'
                    itemsHTML += '</td></tr>'
            
            
            itemsHTML += '</tbody></table></div>'

            itemsHTML += '</div><br/>'

        itemsHTML += '<div class="row text-end">'

        itemsHTML += '<div class="col-md-12 p-5">'
        itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveCalendar(' + str(workorder.id) + ',0,0)">Save</button>'                
        itemsHTML += '</div>'                            
            
        itemsHTML += '</div>'
            
        # itemsHTML += '<script>$("#modalCommentDelete").hide(); $("#divModalDialog").removeClass("mw-650px").addClass("mw-900px"); </script>'

        itemsHTML += '</form>'

    # Tareas particulares
    else:

        calendar = CalendarTask.objects.filter(id=id).first()              
        
        if calendar:
            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %H:%M')
                fechaDate_inicio = fecha_inicio[11:16]

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%m/%d/%Y %H:%M')
                fechaDate_fin = fecha_fin[11:16]

            if calendar.allday:
                allDay = True                

            if calendar.responsible:
                responsibleId = calendar.responsible.id

            if calendar.status:
                status = calendar.status

        itemsHTML += '<form id="formTask_' + str(id) + '" method="POST" enctype="multipart/form-data">'


        itemsHTML += '<div class="row">' 
                        
        itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="30%">Responsible</th><th width="50%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'
        
        itemsHTML += '<tr><td>'
        itemsHTML += '<select class="form-select form-select-sm form-select-solid selectResponsible" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="responsible">'
        itemsHTML += htmlResponsibleSelect(responsibleId)
        itemsHTML += '</select>'
        itemsHTML += '</td><td>'
        
        # Date Start - End
        
        itemsHTML += '<table><tr><td>'
        
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateA" name="dateA" placeholder="Start" value="' + fecha_inicio + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += getDateSelect(name='dateA2', id='dateA2', classAdd='hour-picker', selected = fechaDate_inicio, checked = allDay) #'<input class="form-control form-control-solid timepicker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '-'        
        itemsHTML += '</td><td>'
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += getDateSelect(name='dateB2', id='dateB2', classAdd='hour-picker' , selected = fechaDate_fin, checked = allDay) #'<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'

        itemsHTML += '<tr><td class="p-3 text-start" colspan=5>'

        checked = ''
        if allDay:
            checked += 'checked'        

        itemsHTML += f'<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem" {checked}>'
        
        itemsHTML += '<label class="form-check-label text-gray-700 fw-bold px-3">  All day</label>'
        itemsHTML += '</td></tr></table>'
        
                        
        itemsHTML += '</td><td>'
        itemsHTML += htmlStatusCalendar(status, fecha_fin, calendar, 'statusDate')
        itemsHTML += '</td></tr>'

        itemsHTML += '</tbody></table>'

        itemsHTML += '</div>'

        itemsHTML += htmlDivCommentCalendar()

        itemsHTML += '<br/>'

        itemsHTML += htmlDataCommentCalendar(request, workorder, item, id, 1)
                
        itemsHTML += '<br/>'        

        itemsHTML += '<div class="row text-end">'

        itemsHTML += '<div class="col-md-12 p-5">'
        itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveCalendar(0,0,' + str(id) + ')">Save</button>'
        itemsHTML += '</div>'                            
        
        itemsHTML += '</div>'
        
        # itemsHTML += '<script>$("#modalCommentDelete").hide(); $("#divModalDialog").removeClass("mw-650px").addClass("mw-900px"); </script>'

        itemsHTML += '</form>'
        
            
    itemsHTML += '</div>'    

    return itemsHTML


##################################
## Funciones para Guardar ###
##################################


#Instancia para guardar los datos del calendario para los items de una wo
def saveCalendarItems(request):

    ids = request.POST.getlist('id[]')
    responsibles = request.POST.getlist('responsible[]')
    dates_start = request.POST.getlist('dateItemA[]')
    dates_end = request.POST.getlist('dateItemB[]')
    dates_start_hour = request.POST.getlist('dateItemA2[]')
    dates_end_hour = request.POST.getlist('dateItemB2[]')
    checkAllDays = request.POST.getlist('checkAllDayItem[]')
    statuss = request.POST.getlist('statusDate[]')

    for index, id in enumerate(ids):     

        calendar = CalendarItem.objects.filter(item__id = id).first()
        responsible = Responsible.objects.filter(id = responsibles[index]).first()
        dateStart_get = dates_start[index]
        dateEnd_get = dates_end[index]
        dateStartHour_get = dates_start_hour[index]
        dateEndHour_get = dates_end_hour[index]
        checkAllDay = checkAllDays[index]
        status = statuss[index]

        dateStart = ''
        dateEnd = ''


        if dateStart_get != '' and dateStart_get is not None:
            # Es necesario dar formato a la fecha
            
            if dateEnd_get == '' or dateEnd_get is None:
                dateEnd_get = dateStart_get

            if dateStartHour_get == '' or dateStartHour_get == None:
                dateStartHour_get = ' 00:00' 

            if dateEndHour_get == '' or dateEndHour_get == None:
                dateEndHour_get = ' 23:59' 

            if checkAllDay and checkAllDay == '1':
                dateStart_get += ' 00:00'
                dateEnd_get += ' 23:59'
                checkAllDay = True
            else:
                dateStart_get += ' ' + dateStartHour_get
                dateEnd_get += ' ' + dateEndHour_get
                checkAllDay = False
            
            #dateStart = datetime.strptime(dateStart_get, "%m/%d/%Y %I:%M %p")
            #dateEnd = datetime.strptime(dateEnd_get, "%m/%d/%Y %I:%M %p")

            dateStart = datetime.strptime(dateStart_get, "%m/%d/%Y %H:%M")
            dateEnd = datetime.strptime(dateEnd_get, "%m/%d/%Y %H:%M")

        else:
            dateStart = None
            dateEnd = None


        if calendar:
            if responsible:
                if calendar.responsible:
                    if str(calendar.responsible.id) != responsibles[index]:
                        calendar.responsible = responsible
                else:
                    calendar.responsible = responsible
            
            calendar.date_start = dateStart
            calendar.date_end = dateEnd
            
            if status and str(calendar.status) != status:
                calendar.status = status

            calendar.allday = checkAllDay
            calendar.modification_by_user = request.user.id
            calendar.modification_date = datetime.now()

            calendar.save()

        else:

            CalendarItem.objects.create(    item = Item.objects.filter(id = id).first(),
                                            date_start = dateStart,
                                            date_end = dateEnd,
                                            allday = checkAllDay,
                                            status = 1,
                                            responsible = responsible,
                                            created_by_user = request.user.id,
                                            modification_by_user = request.user.id)


#Instancia para guardar los comentarios de un item o una wo
def saveCalendarComments(request, calendar, item, workorder):

    ids = request.POST.getlist('id[]')
    comments = request.POST.getlist('comment[]')
    commentsFiles = request.FILES.getlist('commentFile[]')
    commentsFilesOk = request.POST.getlist('commentFileOk[]')
    indexFile = 0

    for index, comment in enumerate(comments):
        file = None
        fileName = None

        if comment.strip() != "":

            if item:
                
                calendar_item_comment = CalendarItemComment.objects.create( calendar_item = calendar,
                                                                            notes = comment,
                                                                            created_by_user = request.user.id,
                                                                            modification_by_user = request.user.id)
            
            elif workorder:
                
                calendar_workorder_comment = CalendarWorkOrderComment.objects.create(  calendar_workorder = calendar,
                                                                                        notes = comment,
                                                                                        created_by_user = request.user.id,
                                                                                        modification_by_user = request.user.id)
                

            elif item is None and workorder is None:
                
                calendar_task_comment = CalendarTaskComment.objects.create( calendar_task = calendar,
                                                                            notes = comment,
                                                                            created_by_user = request.user.id,
                                                                            modification_by_user = request.user.id)


            try:
                if int(commentsFilesOk[index]) == 1:
                    file = commentsFiles[indexFile]
                    indexFile += 1
                    fileName = file.name
                        
                    if file:
                        if validateTypeFile(file.content_type):
                            pass
                        else:
                            file = None
                            fileName = ''


                    if item:
                
                        CalendarItemCommentFile.objects.create( calendar_item_comment = calendar_item_comment,
                                                                file = file,
                                                                name = fileName)
                    
                    elif workorder:
                        
                        CalendarWorkOrderCommentFile.objects.create(    calendar_workorder_comment = calendar_workorder_comment,
                                                                        file = file,
                                                                        name = fileName)
                        

                    elif item is None and workorder is None:
                        
                        CalendarTaskCommentFile.objects.create( calendar_task_comment = calendar_task_comment,
                                                                file = file,
                                                                name = fileName)
                
                    
            except:
                
                messages.error(request, 'File not found!')