from django.contrib import messages
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q, Count # permite realizar consultas complejas / Count permite agrupar consultas
from django.utils import timezone #Para ver la hora correctamente.

from ..models import Customer, ProyectDecorator, CalendarItem, CalendarWorkOrder, CalendarTask, CalendarTaskComment, WorkOrder, ItemMaterial, Item, CategoryAttribute, ItemAttribute, AttributeOption, ItemAttributeNote, ItemImage, ItemFile, Subcategory, Category, Group
from ..services.proyect_service import modalComment, modalCalendar, getDataWOs, getCustomer
from ..utils.utils import getDecoratorsTable, newWO




@login_required
def getDataCustomer(request):
    # Verifica si la solicitud es por POST y si tiene el parámetro 'input_value'
    input_value = request.POST.get('address', None)

    customer = Customer.objects.filter(address = input_value).first()

    if customer:        
        datos = {
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'description': customer.description,
            'id': customer.id,
        }
        return JsonResponse(datos)
    else:
        datos = {
            'name': '',
            'email': '',
            'phone': '',
            'description': '',
            'id': '',
        }
        return JsonResponse(datos)


#Consulta ejecutada al momento de crear proyecto y en el detalle del proyecto, para ver la información del decorador/ayudante
@login_required
def getDataDecorator(request):
    #Consulta los decoradores desde la base de datos
    selected_values_str = request.POST.get('idsSelect')
    selected_values = selected_values_str.split(',')
    selected_values = [int(id_value) for id_value in selected_values]
     
    # print("Valores recibidos: ", selected_values)

    decorators = ProyectDecorator.objects.filter(id__in =selected_values)    
        
    decoratorsHTML = getDecoratorsTable(decorators)
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


#Consulta ejecutada para validar la existencia de la direccion
@login_required
def getAddress(request):

    condicionesCustomer = Q()    
    customer_data = []    

    if request.method == 'POST':       

        address = str(request.POST.get('address')).strip()
        city = str(request.POST.get('city')).strip()
        state = str(request.POST.get('state')).strip()
        zipcode = str(request.POST.get('zipcode')).strip()
        apartment = str(request.POST.get('apartment')).strip()

        if address.strip() != '' and len(address) >= 3:
            condicionesCustomer = Q(address__icontains = address) & (Q(city__icontains = city) | Q(state__icontains = state) | Q(zipcode__icontains = zipcode) | Q(apartment__icontains = apartment))
            customer_data = getCustomer(condicionesCustomer, 1)

    messageHtml = ""
   
    exist = ''
    
    if len(customer_data) > 0:

        # Creamos una lista con los datos de cada proyecto
        messageHtml = '<br/><div class="alert alert-warning d-flex align-items-center p-5"><div class="d-flex flex-column"><span><b>Note:</b> There is already a project for that address.</span></div></div>'
        
        messageHtml += '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-6 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
        messageHtml += '<th title="Field #1">Client</th>'
        messageHtml += '<th title="Field #2">Address</th>'
        messageHtml += '<th title="Field #3">Apt-ste-floor</th>'
        messageHtml += '<th title="Field #4">City</th>'
        messageHtml += '<th title="Field #5">State</th>'
        messageHtml += '<th title="Field #6">ZIP code</th>'
        messageHtml += '<th title="Field #7"></th>'
        messageHtml += '<th title="Field #8"></th>'
        messageHtml += '</tr></thead><tbody>'        
                    
        for customer in customer_data:

            msgExist = ''
            if customer['id_proyect'] != '':

                if address == str(customer['address']).strip() and city == str(customer['city']).strip() and state == str(customer['state_u']).strip() and zipcode == str(customer['zipcode']).strip() and apartment == str(customer['apartment']).strip():
                    msgExist = '<span class="badge badge-light-danger fw-bold me-1">Exists!</span>'
                    exist = '1'

                messageHtml += '<tr>'
                messageHtml += '<td>' + customer['customerName'] + '</td>'
                messageHtml += '<td>' + customer['address'] + '</td>'
                messageHtml += '<td>' + str(customer['apartment']) + '</td>'
                messageHtml += '<td>' + str(customer['city']) + '</td>'
                messageHtml += '<td>' + str(customer['state_u']) + '</td>'
                messageHtml += '<td>' + str(customer['zipcode']) + '</td>'
                messageHtml += '<td>' + msgExist + '</td>'
                messageHtml += '<td><a href="../view/' + customer['id_proyect'] + '" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm me-1"><span class="svg-icon svg-icon-3"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M21.4 8.35303L19.241 10.511L13.485 4.755L15.643 2.59595C16.0248 2.21423 16.5426 1.99988 17.0825 1.99988C17.6224 1.99988 18.1402 2.21423 18.522 2.59595L21.4 5.474C21.7817 5.85581 21.9962 6.37355 21.9962 6.91345C21.9962 7.45335 21.7817 7.97122 21.4 8.35303ZM3.68699 21.932L9.88699 19.865L4.13099 14.109L2.06399 20.309C1.98815 20.5354 1.97703 20.7787 2.03189 21.0111C2.08674 21.2436 2.2054 21.4561 2.37449 21.6248C2.54359 21.7934 2.75641 21.9115 2.989 21.9658C3.22158 22.0201 3.4647 22.0084 3.69099 21.932H3.68699Z" fill="black" /><path d="M5.574 21.3L3.692 21.928C3.46591 22.0032 3.22334 22.0141 2.99144 21.9594C2.75954 21.9046 2.54744 21.7864 2.3789 21.6179C2.21036 21.4495 2.09202 21.2375 2.03711 21.0056C1.9822 20.7737 1.99289 20.5312 2.06799 20.3051L2.696 18.422L5.574 21.3ZM4.13499 14.105L9.891 19.861L19.245 10.507L13.489 4.75098L4.13499 14.105Z" fill="black" /></svg></span></a></td>'
                messageHtml += '</tr>'
    
        messageHtml += '</tbody></table>'
        messageHtml += ''
    
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': messageHtml, 'msg': exist})


# Consulta realizada en el panel, para obtener los datos para el calendario
@login_required
def getDataCalendar(request):
    #Consulta los items desde la BD    
    calendarItems = CalendarItem.objects.filter(date_start__isnull=False, status__in = [1, 2])
    calendarWorks = CalendarWorkOrder.objects.filter(date_start__isnull=False, status__in = [1, 2])
    calendarTasks = CalendarTask.objects.filter(date_start__isnull=False, status__in = [1, 2])
    events = []    
    
    # Fechas de los items
    for calendar in calendarItems:
        
        className = 'item'
        fecha_inicio = ''
        fecha_fin = ''
        allDay = False
        color = ''
        responsible = ''

        if calendar.date_start:

            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%Y-%m-%d %H:%M')

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%Y-%m-%d %H:%M')

            if calendar.allday:
                 allDay = True

            if calendar.status == 2:
                # className = 'itemCompleted'
                className = 'completed'

            # if calendar.date_end and calendar.status != 2:
            #     if calendar.date_end < timezone.now():
            #         className = 'overdue'

            if calendar.responsible:
                color = calendar.responsible.color

                if calendar.responsible.name:
                    responsible = calendar.responsible.name

        

            events.append({
                'id': calendar.id,
                'title': calendar.item.workorder.proyect.customer.address,
                'start': fecha_inicio,
                'end': fecha_fin,
                'allDay': allDay,
                'descriptionA': calendar.item.workorder.proyect.customer.name,
                'descriptionB': responsible,
                'color': color,
                'p': str(calendar.item.workorder.proyect.id),
                'w': str(calendar.item.workorder.id),
                'i': str(calendar.item.id),
                'm': 1, # modo 1: item o wo
                'className': className
            })

    for calendar in calendarWorks:
            
        className = ''
        fecha_inicio = ''
        fecha_fin = ''
        allDay = False
        color = ''

        if calendar.date_start:

            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%Y-%m-%d %H:%M')

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%Y-%m-%d %H:%M')

            if calendar.allday:
                allDay = True

            if calendar.status == 2:
                className = 'completed'

            if calendar.date_end and calendar.status != 2:
                if calendar.date_end < timezone.now():
                    className = 'overdue'

            if calendar.responsible:
                color = calendar.responsible.color
                
                if calendar.responsible.name:
                    responsible = calendar.responsible.name
                    
            events.append({
                'id': calendar.id,
                # 'title':  '✅' + wo.proyect.customer.address,
                'title': calendar.workorder.proyect.customer.address,
                'start': fecha_inicio,
                'end': fecha_fin,
                'allDay': allDay,                
                'descriptionA': calendar.workorder.proyect.customer.name,
                'descriptionB': responsible,
                'color': color,          
                'p': str(calendar.workorder.proyect.id),
                'w': str(calendar.workorder.id),
                'i': 0,
                'm': 1, # modo 1: item o wo
                'className': className
            })
                    
    for calendar in calendarTasks:
            
        className = ''
        fecha_inicio = ''
        fecha_fin = ''
        allDay = False
        color = ''
        description = ''

        comment = CalendarTaskComment.objects.filter(calendar_task = calendar).order_by('id').first()

        title = ''
        
        if calendar.responsible:
            title += calendar.responsible.name

        if comment:
            title += ': ' + comment.notes


        if calendar.date_start:

            if calendar.date_start:
                fecha_inicio = timezone.localtime(calendar.date_start).strftime('%Y-%m-%d %H:%M')

            if calendar.date_end:
                fecha_fin = timezone.localtime(calendar.date_end).strftime('%Y-%m-%d %H:%M')

            if calendar.allday:
                allDay = True

            if calendar.status == 2:
                className = 'completed'

            if calendar.date_end and calendar.status != 2:
                if calendar.date_end < timezone.now():
                    className = 'overdue'

            if calendar.responsible:
                color = calendar.responsible.color

            if calendar.responsible:
                description = calendar.responsible.name
                    
            events.append({
                'id': calendar.id,
                # 'title':  '✅' + wo.proyect.customer.address,
                'title': title,
                'start': fecha_inicio,
                'end': fecha_fin,
                'allDay': allDay,
                'description': description,
                'color': color,          
                'p': 0,
                'w': 0,
                'i': 0,
                'm': 2, # modo 2: task
                'className': className
            })

    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'calendar': events})
    

#Funcion para agregar/editar comentarios generales o particulares
@login_required
def getDataModal(request):
    
    workOrderId = request.GET.get('id1')
    itemId = request.GET.get('id2')
    id = request.GET.get('id3')
    case = request.GET.get('id4')

    title = ''
    
    try:
    
        if case == '0': #Comentario
            itemHtml = modalComment(workOrderId, itemId,id)

            wo = WorkOrder.objects.filter(id = workOrderId).first()

            if wo:
                title = wo.state.modalTitle

        elif case == '1' or case == '2': #Calendario 1: wo/item -  2: tasks
            itemHtml = modalCalendar(request, workOrderId, itemId, id)
            title = 'Calendar'
        else:
            itemHtml = 'Server error. Please contact to administrator!'            
    
    except:

        itemHtml = 'Server error. Please contact to administrator!'
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': itemHtml, 'title': title})


#Funcion autocomplete de materiales por Ajax, para crear un item.
@login_required
def getDataMaterial(request):
    # Verifica si la solicitud es por POST y si tiene el parámetro 'input_value'
    input_value = request.GET.get('term', None)
    materials = ItemMaterial.objects.filter(notes__icontains=input_value).order_by('notes').values_list('notes', flat=True).distinct()[:100]

   # materials ya es una lista de strings, no objetos
    results = list(materials)

    return JsonResponse(results, safe=False)


#Funcion que carga los datos del item
@login_required
def getDataItem(request):
    
    workorderId = request.POST.get('w', None)
    itemId = request.POST.get('i', None)

    wo = WorkOrder.objects.get(id=workorderId)
    item = Item.objects.get(id = itemId, workorder = wo)

    ######### Atributos ##########

    categoryAttributes = CategoryAttribute.objects.filter(category = Category.objects.get(id = item.subcategory.category.id)).order_by('order','attribute')

    attributeHTML = ""
        
    for category in categoryAttributes:
        attributeHTML += '<div class="row mb-2">'
        attributeHTML += '<div class="col-xl-3"><div class="fs-7 fw-bold mt-2 mb-3">' + category.attribute.name + ':</div></div>'
        notes = ''        

        itemAttribute = ItemAttribute.objects.filter(item = item, attribute = category.attribute).first()

        if itemAttribute:
            notes = itemAttribute.notes              

        if category.attribute.multiple:
            options = AttributeOption.objects.filter(attribute = category.attribute)
            optionsSelected = ItemAttributeNote.objects.filter(itemattribute = itemAttribute)

            attributeHTML += '<div class="col-xl-8"><select class="form-select form-select-sm form-select-solid selectAttribute" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="true" name="attribute_' + str(category.attribute.id) + '" multiple>'
                
            for option in options:
                selected = ''

                if optionsSelected.filter(attributeoption=option).exists():
                    selected = 'selected'
                    
                if option.file:
                    attributeHTML += '<option value=' + str(option.id) + ' data-image="' + str(option.file.url) + '" ' + selected + '>' + option.name + '</option>'
                else:
                    attributeHTML += '<option value=' + str(option.id) + ' data-image="/static/images/no-image.png" ' + selected + '>' + option.name + '</option>'

            attributeHTML += '</select></div>'

            attributeHTML += '<div id="image-tooltip" style="position: absolute; display: none; border: none; background: none; padding: 5px; z-index: 9999;"><img src="" id="tooltip-img" style="max-height: 300px;" /></div>'
            
        else:                                      
            attributeHTML += '<div class="col-xl-8"><input name="attribute_' + str(category.attribute.id) + '" type="text" class="form-control form-control-solid" maxlength="150" placeholder="' + category.attribute.description + '" value="' + notes + '"/></div>'

        attributeHTML += '</div>'
    
    ##############################

    spanHTML = '<span class="svg-icon svg-icon-2">'
    spanHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    spanHTML += '<path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" />'
    spanHTML += '<path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" />'
    spanHTML += '<path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" />'
    spanHTML += '</svg>'
    spanHTML += '</span>'


    ######### Matariales #########
    
    materialsHTML = ""
                                
    itemMaterials = ItemMaterial.objects.filter(item=item).order_by('id')
    materialsHTML += ''
    
    for itemMaterial in itemMaterials:

        fileUrl = ''
        style = 'style="display:none"'
        qty = ''
        qtyR = ''
        dateR = ''
        img = ''
        fileName = ''
        id = '0'

        if itemMaterial.file:
            fileUrl = itemMaterial.file.url
            fileName = itemMaterial.name
            img = '<img class="preview" src="' + fileUrl + '" alt="Preview" style="display:none"><div class="symbol symbol-100px mb-5 fileUpload">'

            if fileUrl[-4:] == '.pdf':
                img += '<img alt="" class="w-60px me-3" src="/static/images/pdf.svg" alt=""><a href="' + fileUrl + '" class="fs-7 text-hover-primary" target="_blank">' + fileName + '</a>'

            elif fileUrl[-5:] == '.docx' or fileUrl[-4:] == '.doc':
                img += '<img alt="" class="w-60px me-3" src="/static/images/doc.svg" alt=""><a href="' + fileUrl + '" class="fs-7 text-hover-primary" target="_blank">' + fileName + '</a>'

            elif fileUrl[-5:] == '.xlsx' or fileUrl[-4:] == '.xls':
                img += '<img alt="" class="w-60px me-3" src="/static/images/xls.svg" alt=""><a href="' + fileUrl + '" class="fs-7 text-hover-primary" target="_blank">' + fileName + '</a>'
            
            elif fileUrl[-5:] == '.pptx' or fileUrl[-4:] == '.ppt':
                img += '<img alt="" class="w-60px me-3" src="/static/images/ppt.svg" alt=""><a href="' + fileUrl + '" class="fs-7 text-hover-primary" target="_blank">' + fileName + '</a>'
            
            else:
                img = '<img class="preview" src="' + fileUrl + '" alt="Preview"><div class="symbol symbol-100px mb-5 fileUpload" style="display:none"><img src="/static/images/upload.svg" alt="">'

            
        if itemMaterial.qty:
            qty = itemMaterial.qty

        if itemMaterial.qty_received:
            qtyR = itemMaterial.qty_received

        if itemMaterial.date_received:
            dateR = itemMaterial.date_received

        if itemMaterial.id:
            id = str(itemMaterial.id)

        materialsHTML += '<tr class="baseRow">'
        materialsHTML += '<td valign="top"><input type="text" name="material[]" class="form-control form-control-solid autocompleteMaterial" value="' + itemMaterial.notes + '"></td>'
        materialsHTML += '<td valign="top"><input type="text" name="materialQTY[]" class="form-control form-control-solid" value="' + qty + '"></td>'
        materialsHTML += '<td valign="top"><input type="text" name="materialRQTY[]" class="form-control form-control-solid" value="' + qtyR + '"></td>'
        materialsHTML += '<td valign="top"><input type="text" name="materialDate[]" class="form-control form-control-solid materialDate" value="' + dateR + '"></td>'
        materialsHTML += '<td valign="top" class="text-center"><input type="file" name="materialFile[]" class="form-control form-control"><input type="hidden" name="materialFileOk[]"></td>'
        materialsHTML += '<td valign="top" class="text-center">' + img + '</div></td>'
        materialsHTML += '<td valign="top" class="text-center">'
        materialsHTML += '<div class="btn btn-icon btn-sm btn-color-gray-400 btn-active-icon-danger me-2 deleteMaterial" data-bs-toggle="tooltip" data-bs-dismiss="click" title="Delete">'
        materialsHTML += '<input type="hidden" name="materialIds[]" class="form-control form-control-solid" value="MAT_' + id + '">'
        materialsHTML += spanHTML

        materialsHTML += '</div>'
        materialsHTML += '</td>'
        materialsHTML += '</tr>'

    ##############################

    ########## Imagenes ##########


    itemImages = ItemImage.objects.filter(item=item).order_by('id')
    imagesHTML = ''
    
    for itemImag in itemImages:

        fileUrl = ''
        style = 'style="display:none"'
        style2 = 'style="display:none"'
        qty = ''
        id = '0'

        if itemImag.file:
            fileUrl = itemImag.file.url
            style = ''
        else:
            style2 = ''

        if itemImag.id:
            id = str(itemImag.id)
        
        imagesHTML += '<tr class="baseRowImage">'
        imagesHTML += '<td valign="top"><textarea name="image[]" class="form-control form-control-solid h-80px" maxlength="2000">' + itemImag.notes + '</textarea></td>'        
        imagesHTML += '<td valign="top" class="text-center"><input type="file" name="imageFile[]" class="form-control form-control"><input type="hidden" name="imageFileOk[]"></td>'
        imagesHTML += '<td valign="top" class="text-center"><img class="preview" src="' + fileUrl + '" alt="Preview" ' + style + '><div class="symbol symbol-100px mb-5 fileUpload" ' + style2 + ' ><img src="/static/images/upload.svg" alt=""></div></td>'
        imagesHTML += '<td valign="top" class="text-center"><div class="btn btn-icon btn-sm btn-color-gray-400 btn-active-icon-danger me-2 deleteImage" data-bs-toggle="tooltip" data-bs-dismiss="click" title="Delete">'
        imagesHTML += '<input type="hidden" name="imageIds[]" class="form-control form-control-solid" value="IMG_' + id + '">'
        imagesHTML += spanHTML																								
        imagesHTML += '</div>'
        imagesHTML += '</td>'
        imagesHTML += '</tr>'


    itemImages = ItemFile.objects.filter(item=item).order_by('id')
        
    for itemImag in itemImages:

        fileUrl = ''
        fileName = ''
        style = 'style="display:none"'
        img = ''
        id = '0'

        if itemImag.file:
            fileUrl = itemImag.file.url
            fileName = itemImag.name
            style = ''

            if fileUrl[-4:] == '.pdf':
                img = '<img alt="" class="w-60px me-3" src="/static/images/pdf.svg" alt=""><br/>'

            elif fileUrl[-5:] == '.docx' or fileUrl[-4:] == '.doc':
                img = '<img alt="" class="w-60px me-3" src="/static/images/doc.svg" alt=""><br/>'

            elif fileUrl[-5:] == '.xlsx' or fileUrl[-4:] == '.xls':
                img = '<img alt="" class="w-60px me-3" src="/static/images/xls.svg" alt=""><br/>'

            elif fileUrl[-5:] == '.pptx' or fileUrl[-4:] == '.ppt':
                img = '<img alt="" class="w-60px me-3" src="/static/images/ppt.svg" alt=""><br/>'
            
            else:
                img = '<img src="/static/images/upload.svg" alt=""><br/>'

        if itemImag.id:
            id = str(itemImag.id)


        imagesHTML += '<tr class="baseRowImage">'
        imagesHTML += '<td valign="top"><textarea name="image[]" class="form-control form-control-solid h-80px" maxlength="2000">' + itemImag.notes + '</textarea></td>'        
        imagesHTML += '<td valign="top" class="text-center"><input type="file" name="imageFile[]" class="form-control form-control"><input type="hidden" name="imageFileOk[]">'
        imagesHTML += '<td valign="top" class="text-center"><img class="preview" src="" alt="Preview" style="display:none"><div class="symbol symbol-100px mb-5 fileUpload" ' + style + '>' + img +'<a href="' + fileUrl + '" class="fs-7 text-hover-primary" target="_blank">' + fileName + '</a></div></td>'
        imagesHTML += '<td valign="top" class="text-center"><div class="btn btn-icon btn-sm btn-color-gray-400 btn-active-icon-danger me-2 deleteImage" data-bs-toggle="tooltip" data-bs-dismiss="click" title="Delete">'
        imagesHTML += '<input type="hidden" name="imageIds[]" class="form-control form-control-solid" value="FIL_' + id + '">'
        imagesHTML += spanHTML																								
        imagesHTML += '</div>'
        imagesHTML += '</td>'
        imagesHTML += '</tr>'

    ###########################
    
    groupId = '0'

    if item.group:
        groupId = item.group.id

    
    placeId = '0'
    if item.place:
        placeId = item.place.id

    
    date_proposed = ''
    if item.date_proposed:
        if item.date_proposed != '':
            date_proposed = item.date_proposed.strftime("%m/%d/%Y")

    response_data = {}    

    if item:
        response_data = {
            'category': item.subcategory.category.id,
            'subCategory': item.subcategory.id,
            'group': groupId,
            'place': placeId,
            'qty': item.qty,
            'date': date_proposed,
            'notes': item.notes,
            'attributes': attributeHTML,
            'materials': materialsHTML,
            'images': imagesHTML,
        }

    return JsonResponse(response_data)


#Funcion para agregar una WO
@login_required
def addWorkOrder(request):
    proyectId = request.POST.get('p')    
    result = newWO(request, proyectId)
    workorderId = -1

    if result:
        workorderId = result.id

        try: 
            if 'stateId' in request.session:
                del request.session['stateId']
        except:
            None
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': workorderId})


#Funcion para agregar comentarios a la WO
@login_required
def getDataWO(request):
    
    workOrderId = request.GET.get('id1')
    woHTML = ''
               
    try:    

        wo = WorkOrder.objects.filter(id=workOrderId).first()

        woHTML += '<div class="col-xl-12 fv-row text-start">'      
        woHTML += '<form id="formWO" method="POST">'
            
        woHTML += '<div class="fs-7 fw-bold mt-2 mb-3">Notes:</div>'
        woHTML += '<textarea name="notes" class="form-control form-control-solid h-80px" maxlength="2000">' + str(wo.description) + '</textarea><br/>'
        woHTML += '<input type="hidden" name="woId" value="' + workOrderId + '">'
        woHTML += '</div>'

        woHTML += '<div class="row text-end">'

        woHTML += '<div class="col-md-12">'
        woHTML += '<button type="button" class="btn btn-primary btn-sm px-8 py-2 mr-2" onclick="saveWO()">Download PDF</button>'
        woHTML += '<a id="linkPDF"  href="../../generate_pdf/' + workOrderId + '" target="_blank"></a>'
        woHTML += '</div>'    
                    
                                    
        woHTML += '</div>'

          
    except:
         woHTML = 'Server error. Please contact to administrator!'
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': woHTML})


#Funcion para validar el avance entre los estados. Se gestionan los mensajes positivos y negativos
@login_required
def getStateValidate(request):
    
    workOrderId = request.POST.get('w')
    status = 0
    message = ''
               
    try:    

        wo = WorkOrder.objects.filter(id=workOrderId).first()
        items = Item.objects.filter(workorder=wo)

        itemsC = Item.objects.filter(workorder=wo, itemcommentstate__state_id=wo.state.id).distinct().count()
        itemsG = WorkOrder.objects.filter(id=wo.id, workordercommentstate__state_id=wo.state.id).distinct().count()


        if wo.state.id == 1:
            if len(items) > 0:
                message = wo.state.positiveMessage
                status = 1
            else:
                message = wo.state.negativeMessage

        if wo.state.id == 4:

            has_materials = False

            items = Item.objects.filter(workorder=wo)

            for item in items:
                has_materials = ItemMaterial.objects.filter(item=item).exists()
            
            todos_completos = all(ItemMaterial.objects.filter(
                                        item=item,
                                        date_received__isnull=False,
                                        qty_received__isnull=False
                                    ).exclude(
                                        date_received='',
                                        qty_received=''
                                    ).exists()
                                    for item in items
                                )

            if has_materials and todos_completos:
                message = wo.state.positiveMessage
                status = 1
            else:
                message = wo.state.negativeMessage  


        if wo.state.id in (2,3,5,6,7,8,9,10):

            if len(items) == itemsC or itemsG > 0:
                message = wo.state.positiveMessage
                status = 1
            else:
                message = wo.state.negativeMessage        

          
    except:
        message = 'Server error. Please contact to administrator!'
        status = 0
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result1':status, 'result2': message})






###############################
### Elementos dependientes  ###
###############################

#Consulta ejecutada al crear proyecto
@login_required
def selectAscociate(request):
    #Consulta los decoradores desde la base de datos
    selected_values_str = request.POST.get('decoratorsSelect')
    selected_values = selected_values_str.split(',')
    selected_values = [int(id_value) for id_value in selected_values]     

    supervisors = ProyectDecorator.objects.filter(id__in =selected_values,is_supervisor=1)
    decorators = ProyectDecorator.objects.filter(supervisor__in = supervisors).order_by('name')

    decoratorsHTML = ''

    for decorator in decorators:  
        # print("Valores recibidos: ", decorator.id )
        decoratorsHTML += '<option value=' + str(decorator.id) + '>' + decorator.name + '</option>'
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


#Consulta ejecutada al crear un item
@login_required
def selectSubcategory(request):
    #Consulta las subcategorias desde la base de datos
    selected_value = request.POST.get('categorySelect').strip()
    subcategoryHTML = ''

    try:

        if selected_value.isdigit():

            subcategories = Subcategory.objects.filter(category = Category.objects.get(id = selected_value)).order_by('order','name')
        
            for subcategory in subcategories:          
                subcategoryHTML += '<option value=' + str(subcategory.id) + '>' + subcategory.name + '</option>'

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': subcategoryHTML})


#Consulta ejecutada al crear un item
@login_required
def selectGroup(request):
    #Consulta las subcategorias desde la base de datos    
    subcategory_value = request.POST.get('subcategorySelect')
    groupHTML = '<option value=''>---</option>'

    if subcategory_value != '':        

        try:

            if subcategory_value.isdigit():

                groups = Group.objects.filter(subcategory = Subcategory.objects.get(id = subcategory_value)).order_by('order','name')
            
                for group in groups:          
                    groupHTML += '<option value=' + str(group.id) + '>' + group.name + '</option>'

        except ValueError:
            messages.error(request, 'Server error. Please contact to administrator!')
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': groupHTML})


#Consulta ejecutada al crear un item
@login_required
def selectAttibutes(request):
    #Consulta las subcategorias desde la base de datos
    selected_value = request.POST.get('categorySelect').strip()
    attributeHTML = ''

    try:

        if selected_value.isdigit():

            attributes = CategoryAttribute.objects.filter(category = Category.objects.get(id = selected_value)).order_by('order','attribute')
            
            for attribute in attributes:
                attributeHTML += '<div class="row mb-2">'
                attributeHTML += '<div class="col-xl-3"><div class="fs-7 fw-bold mt-2 mb-3">' + attribute.attribute.name + ':</div></div>'

                if attribute.attribute.multiple:
                                    
                    options = AttributeOption.objects.filter(attribute = attribute.attribute)
                    attributeHTML += '<div class="col-xl-8"><select class="form-select form-select-sm form-select-solid selectAttribute" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="true" name="attribute_' + str(attribute.attribute.id) + '" multiple>'
                    
                    for option in options:
                        
                        if option.file:
                            attributeHTML += '<option value=' + str(option.id) + ' data-image="' + str(option.file.url) + '">' + option.name + '</option>'
                        else:
                            attributeHTML += '<option value=' + str(option.id) + ' data-image="/static/images/no-image.png">' + option.name + '</option>'

                    attributeHTML += '</select></div>'

                    attributeHTML += '<div id="image-tooltip" style="position: absolute; display: none; border: none; background: none; padding: 5px; z-index: 9999;"><img src="" id="tooltip-img" style="max-height: 300px;" /></div>'


                else:
                    attributeHTML += '<div class="col-xl-8"><input name="attribute_' + str(attribute.attribute.id) + '" type="text" class="form-control form-control-solid" maxlength="150" placeholder="' + attribute.attribute.description + '"/></div>'

                attributeHTML += '</div>'



    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': attributeHTML})


#Consulta ejecutada en la vista del proyecto y en el panel (vista previa), para ver toda la información de las WO's junto con los items.
@login_required
def selectWOs(request):
    #Consulta los items desde la base de datos
    proyectId = request.POST.get('p')
    stateId = request.POST.get('s')
    mode = request.POST.get('m')
    wosHTML = getDataWOs(request, proyectId, stateId, int(mode))
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': wosHTML})


