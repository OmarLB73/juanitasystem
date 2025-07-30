from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib import messages
from datetime import datetime # dar formato a la fecha
from django.shortcuts import redirect # redireccionar a páginas
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q, Count # permite realizar consultas complejas / Count permite agrupar consultas
from django.urls import reverse #evita doble envio de formulario

# from django.core.files.storage import FileSystemStorage #para las imagenes

from PIL import Image #Para validar el tipo de imagen
from django.core.exceptions import ValidationError #Para manejar excepciones

from django.utils import timezone #Para ver la hora correctamente.

from xhtml2pdf import pisa #Para el PDF
from django.template.loader import get_template #Para el PDF
from django.http import Http404 #Para el PDF
from django.conf import settings #Para el PDF, manejar las rutas

from django.http import HttpRequest #Para las sesiones

from django.contrib.auth.models import User #Datos del usuario
from .models import Type, Responsible, Customer, State, Proyect, ProyectDecorator, Event, Category, Subcategory, Place, CategoryAttribute, Attribute, Item, ItemAttribute, ItemImage, Group, ItemFile, ItemCommentState, ItemCommentStateFile, WorkOrder, ItemMaterial, WorkOrderCommentState, WorkOrderCommentStateFile, UIElement, AttributeOption, ItemAttributeNote, CalendarItem, CalendarWorkOrder, CalendarItemComment, CalendarItemCommentFile, CalendarWorkOrderComment, CalendarWorkOrderCommentFile, CalendarTask, CalendarTaskComment, CalendarTaskCommentFile #Aquí importamos a los modelos que necesitamos

import ast #Usado para pasar una lista string a lista de verdad


@login_required
def panel_view(request):

    if request.path == '/proyect/calendar/':        
        mode = 'Calendar'
    else:
        # lógica general para panel
        mode = 'Panel'


    try: 
        if 'stateId' in request.session:
            del request.session['stateId']
    except:
        None

    #Consulta los proyectos/tipos/estados desde la base de datos    
    types = Type.objects.filter(status=1).order_by('id')
    states = State.objects.filter(status=1).order_by('id')
    decorators = ProyectDecorator.objects.filter(is_supervisor = 1).order_by('name')

    type_id = 0
    state_id = 0
    decorator_id = 0
    date_from = ''
    date_until = ''    
    condiciones = Q()
    proyects_data = []

    if request.method == 'POST':       

        date_from = request.POST.get('dateFrom')
        date_until = request.POST.get('dateUntil')
        type_id = int(request.POST.get('type'))
        state_id = int(request.POST.get('state'))
        decorator_id = int(request.POST.get('decorator'))

        if date_from != '':
            try:
                date_from_obj = datetime.strptime(date_from, '%m/%d/%Y')  # Convierte el string a datetime
                condiciones &= Q(creation_date__gte=date_from_obj)  # Fecha mayor o igual
            except ValueError:
                pass  # Si hay un error de formato, no se aplica la condición

        if date_until != '':            
            try:
                date_until_obj = datetime.strptime(date_until, '%m/%d/%Y')  # Convierte el string a datetime
                # Concatenamos las horas para asegurarnos de que sea hasta el final del día
                date_until_end = datetime.combine(date_until_obj, datetime.max.time())  # Al final del día
                condiciones &= Q(creation_date__lte=date_until_end)  # Fecha menor o igual
            except ValueError:
                pass  # Si hay un error de formato, no se aplica la condición

        if type_id != 0:
            condiciones &= Q(type__id = type_id) ##igual a fk

        if state_id != 0:
            condiciones &= Q(workorder__state__id = state_id) ##igual a fk

        if decorator_id != 0:
            condiciones &= Q(decoratorProyects__id = decorator_id) ##igual a fk            


    if mode == 'Panel':
        proyects_data = getDataProyect(condiciones)

    uielement = UIElement.objects.all()
    # Crear un diccionario de claves y valores con la key y el label_text
    labels = {element.key: element.label_text for element in uielement}
    
    return render(request, 'proyect/panel.html', {'proyects_data': proyects_data,
                                                  'date_from': date_from,
                                                  'date_until': date_until,
                                                  'type_id': type_id,
                                                  'state_id': state_id,
                                                  'decorator_id': decorator_id,
                                                  'types': types,
                                                  'states': states,
                                                  'decorators': decorators,
                                                  'labels': labels,
                                                  'mode': mode})    


@login_required
def proyect_new(request):
    
    uielement = UIElement.objects.all()
    # Crear un diccionario de claves y valores con la key y el label_text
    labels = {element.key: element.label_text for element in uielement}

    if request.method == 'POST':

        type_id = request.POST.get('type')

        decorators_ids = request.POST.getlist('decorator')
        ascociate_ids = request.POST.getlist('ascociate')
        
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        apartment = request.POST.get('apartment')
            
        customer_description = request.POST.get('addressDescription')        
        customer_name = request.POST.get('customerName')
        customer_notes = request.POST.get('customerDescription')

        email = request.POST.get('email')
        phone = request.POST.get('phone')

        date = request.POST.get('date')                         
        proyect_description = request.POST.get('proyectDescription')


        #Se busca si existe el cliente
        condicionesCustomer = Q()
        condicionesCustomer = Q(address__icontains = address) & Q(city__icontains = city) & Q(state__icontains = state) & Q(zipcode__icontains = zipcode) & Q(apartment__icontains = apartment)
        customer_data = getDataCustomer(condicionesCustomer, 1)

        # Si la direccion no existe por si acaso
        if len(customer_data) == 0:  

            user_id = request.user.id
            state_Id = 1 #Inicio


                #    if Customer.objects.filter(id=customer_id).exists():
                #         customer_save = Customer.objects.get(id=customer_id)
                #         customer_save.name = customer_name
                #         customer_save.email = email
                #         customer_save.phone = phone
                #         customer_save.description = customer_Description
                #         customer_save.save()


            code = ""
            if type_id == '1':
                code = "&"
            
            if type_id == '2':
                code = "#"


            #Se guarda los datos del cliente
            customer_id = 0
            try:

                #Se busca el cliente si existe (hasta ahora, solo por nombre)
                customer = Customer.objects.filter(name=customer_name, phone = phone).first()  # phone es muy importante en USA

                if customer == None:

                    customer_save = Customer.objects.create(name=customer_name, 
                                                            address=address,
                                                            city=city,
                                                            state=state,
                                                            zipcode=zipcode,
                                                            apartment=apartment,                                                    
                                                            email=email,
                                                            phone=phone,
                                                            description=customer_description,
                                                            notes=customer_notes,
                                                            created_by_user = request.user.id,
                                                            modification_by_user = request.user.id
                                                            )
                    
                
                else:
                    customer_save = customer                

                customer_id = customer_save.id

                #Iniciales del nombre, si es a través de Cliente
                if type_id == '1':
                    partes = customer_save.name.split()
                    code += ''.join([parte[0].upper() for parte in partes])


            except ValueError:
                messages.error(request, 'Server error. Please contact to administrator!')
                return render(request, 'proyect/new.html')

            
            # #  Se intenta obtener el responsable 
            # try:
            #     # Intentamos obtener el objeto
            #     responsible = Responsible.objects.get(id=responsible_id),
            # except Responsible.DoesNotExist:
            #     # Si no existe, devolvemos None (equivalente a null en otros lenguajes)
            #     responsible = None


            #Se guarda los datos del proyecto
            proyect_id = 0        

            try:
                if int(type_id) and int(customer_id):
                    proyect_save = Proyect.objects.create(  type=Type.objects.get(id=type_id), 
                                                            customer=Customer.objects.get(id=customer_id), 
                                                            # responsible=responsible,
                                                            #state=State.objects.get(id=state_Id),
                                                            # date=date, 
                                                            description=proyect_description,                                                        
                                                            created_by_user = request.user.id,
                                                            modification_by_user = request.user.id)
                    proyect_id = proyect_save.id

                    

                    for decorator_id in decorators_ids:
                        decorator = ProyectDecorator.objects.get(id = decorator_id)
                        decorator.proyects.add(proyect_save)

                        #Iniciales del nombre, si es através de Cliente
                        if type_id == '2':
                            partes = decorator.name.split()
                            code += ''.join([parte[0].upper() for parte in partes])

                    for decorator_id in ascociate_ids:
                        decorator = ProyectDecorator.objects.get(id = decorator_id)
                        decorator.proyects.add(proyect_save)


                    #Se actualiza el código, una vez que se obtiene el Id.                
                    code += f"{proyect_id:03d}"
                    proyect_save.code =  code
                    proyect_save.save()


                    workorder = newWO(request, proyect_id)                    
                    saveEvent(request, 2, proyect_save, workorder, None, 'Create WO')
            
                    return redirect(reverse('view_url', kwargs={'proyect_id': proyect_id}))

            except ValueError:        
                messages.error(request, 'Server error. Please contact to administrator!')
                return render(request, 'proyect/new.html')

        else:
            messages.error(request, 'The address already exists! Please review the projects.')
            return render(request, 'proyect/new.html')


    else:

        types = Type.objects.filter(status=1).order_by('id')
        # customers = Customer.objects.filter(status=1).order_by('name')
        decorators = ProyectDecorator.objects.filter(is_supervisor=1, status=1).order_by('name')
        type_select = types.first()

        return render(request, 'proyect/new.html', 
                    {'types': types,
                    'type_select': type_select,
                    'decorators': decorators,
                    'labels': labels,
                    })


@login_required
def proyect_view(request, proyect_id):

    stateId = 0
    
    if request.session.get('stateId'):
        try:
            stateId = int(request.session['stateId'])
            # del request.session['stateId']
        except:
            None

    proyect = Proyect.objects.get(id = proyect_id) #obtiene solo un resultado
    customer = proyect.customer    
    category = Category.objects.all().order_by('order','name')
    place = Place.objects.all().order_by('name')
        
    try:
        decorators = ProyectDecorator.objects.filter(proyects = proyect, is_supervisor = 1).order_by('name')
        ascociates = ProyectDecorator.objects.filter(proyects = proyect, is_supervisor = 2).order_by('name')
        #events = Event.objects.filter(proyect_id = proyect_id).order_by('creation_date')

    except ProyectDecorator.DoesNotExist:
        decorators = None
        ascociates = None

    #except Event.DoesNotExist:
        #events = None

    except State.DoesNotExist:
        state_new_name = ''

    workOrdersHtml = getDataWOs(request, proyect_id, stateId, 1)    

    decoratorsHTML = getDecoratorsTable(decorators)
    ascociatesHTML = getDecoratorsTable(ascociates)
    resumenWos = getResumenWOs(request, proyect)
    #notesHTML = funct_data_events(proyect_id)

    uielement = UIElement.objects.all()
    # Crear un diccionario de claves y valores con la key y el label_text
    labels = {element.key: element.label_text for element in uielement}
                        
    return render(request, 'proyect/view.html',{'proyect': proyect,
                                                'customer': customer,
                                                'decorators': decorators,
                                                #'events':events,
                                                'categories':category,
                                                'places': place,
                                                'workOrdersHtml': workOrdersHtml,
                                                'decoratorsHTML': decoratorsHTML,
                                                'ascociatesHTML': ascociatesHTML,
                                                'labels': labels,
                                                'stateId': stateId,
                                                'resumenWos': resumenWos
                                                #'notesHTML': notesHTML,
                                                }) 


@login_required
def grafics_view(request):
    return render(request, 'proyect/grafics.html')    



############################
####### Obtener datos ######
############################

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
            customer_data = getDataCustomer(condicionesCustomer, 1)

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
                    
            events.append({
                'id': calendar.id,
                # 'title':  '✅' + wo.proyect.customer.address,
                'title': title,
                'start': fecha_inicio,
                'end': fecha_fin,
                'allDay': allDay,
                'description': calendar.responsible.name,
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

        if itemMaterial.id:
            id = str(itemMaterial.id)

        materialsHTML += '<tr class="baseRow">'
        materialsHTML += '<td valign="top"><input type="text" name="material[]" class="form-control form-control-solid autocompleteMaterial" value="' + itemMaterial.notes + '"></td>'
        materialsHTML += '<td valign="top"><input type="text" name="materialQTY[]" class="form-control form-control-solid" value="' + qty + '"></td>'        
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
         itemHtml = 'Server error. Please contact to administrator!'
    
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
    selected_value = request.POST.get('categorySelect')
    subcategoryHTML = ''

    try:
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
    selected_value = request.POST.get('categorySelect')    
    attributeHTML = ''

    try:

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


#Consulta ejecutada en el panel, para acceder a la info del proyecto.
@login_required
def saveSessionState(request):
    #Consulta los items desde la base de datos    
    stateId = request.POST.get('s')    
    request.session['stateId'] = stateId

    return JsonResponse({'result': 'OK'})


                    

###################################
## Funciones para obtener datos ###
###################################

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
            workOrdersHTML += '<div class="card card-xxl-stretch mb-8 mb-xl-12">' #BORDE ITEM style="border:1px solid white; border-width:1px;"
            
            #Titulo
            workOrdersHTML += '<div class="card-header pt-5">'
            workOrdersHTML += '<div class="col-lg-12">'

            workOrdersHTML += '<div class="row">'

            #Celda 1
            workOrdersHTML += '<div class="col-lg-7">' #style="border:1px solid red; border-width:1px;"
            
            workOrdersHTML += '<h3 class="card-title align-items-start flex-column">'
            workOrdersHTML += '<span class="card-label fw-bolder fs-3 mb-1">Work Order ' + str(woN) + ':' + getStateName(wo.state.id, '6') + '</span>' 

            #Subtitulo
            workOrdersHTML += '<span class="text-muted mt-1 fw-bold fs-7">' + stateDescription + '</span>'
            workOrdersHTML += '</h3>'

            if wo.state.id == 1 and mode == 1: #Solo si se edita

                workOrdersHTML += '<div class="col-lg-4"><a id="aAddItem" class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalItem" onclick="wo(' + str(wo.id) + ')">Add Item (+)</a></div>'
                
            workOrdersHTML += '</div>'


            #Celda 2
            workOrdersHTML += '<div class="col-lg-3 d-flex flex-column justify-content-end">' #style="border:1px solid green; border-width:1px;"

            if mode == 1:
                workOrdersHTML += '<div class="col-lg-4"><a id="aAddItem" class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,1)">Schedule (+)</a></div>'

            workOrdersHTML += '</div>'


            #Celda 3
            workOrdersHTML += '<div class="col-lg-2 text-end pt-5">' #style="border:1px solid yellow; border-width:1px;"
            
            if wo.state.id < 10 and mode == 1: #Solo si se edita

                 workOrdersHTML += '<a id="aState" href="javascript:state(' + str(wo.id) + ',' + str(wo.state.id) + ')" class="btn btn-sm btn-primary font-weight-bolder text-uppercase" data-bs-toggle="tooltip" title="' + buttonDescription + '">' + buttonName + '</a>'
                 workOrdersHTML += '<input id="stateAfter" type="hidden" value="' + stateNewName + '">'
                                    
            workOrdersHTML += '</div>'

            workOrdersHTML += '</div>'
                    

            workOrdersHTML += '</div></div>'
            #Fin Titulo

            #Lista de Items
            workOrdersHTML += '<div class="card-body" style="padding-top:0">'


            if mode == 1 and len(items) > 0: # Solo si se edita

                if wo.state.id == 2:

                    workOrdersHTML += '<div class="col-xl-2 py-1 fv-row">'
                    workOrdersHTML += '<a class="btn btn-link fs-6 py-1" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)">Add general quote (+)</a>'
                    workOrdersHTML += '</div>'


                if wo.state.id == 3:

                    workOrdersHTML += '<div class="col-xl-2 py-1 fv-row">'
                    workOrdersHTML += '<a class="btn btn-link fs-6 py-1" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)">Add general approve quote (+)</a>'
                    workOrdersHTML += '</div>'

                if wo.state.id >= 4 and wo.state.id <= 9:

                    workOrdersHTML += '<div class="col-xl-2 py-1 fv-row">'
                    workOrdersHTML += '<a class="btn btn-link fs-6 py-1" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(wo.id) + ',0,0,0)">Add general comment (+)</a>'
                    workOrdersHTML += '</div>'

            if wo.state.id >= 5:

                workOrdersHTML += '<div class="col-xl-2 fv-row">'
                if mode == 1:
                    
                    # workOrdersHTML += '<a href="../../generate_pdf/' + str(wo.id) + '" class="fs-6 text-hover-primary" target="_blank">Download WO</a>'
                    workOrdersHTML += '<a id="downloadWO" class="btn btn-link fs-6 py-1" data-bs-toggle="modal" data-bs-target="#modalWO" onclick="loadModalWO(' + str(wo.id) + ')">Download WO</a>'

                else:
                    workOrdersHTML += '<a href="../../proyect/generate_pdf/' + str(wo.id) + '" class="fs-6 text-hover-primary" target="_blank">Download WO</a>'
                workOrdersHTML += '</div>'

                    
            #Detalle de los items
            workOrdersHTML += '<div id="itemsDetails_' + str(wo.id) + '">'
            workOrdersHTML += getDataItems(request, wo.id, mode)
            workOrdersHTML += '</div>'

            #Comentarios genéricos por etapa/estado
            workOrdersHTML += getDataComments(request, wo.id, 0, mode)

            workOrdersHTML += '</div>'
            #Fin item

            workOrdersHTML += '</div>' #Fin BORDE ITEM
            workOrdersHTML += '</div>' #FIN CONTENEDOR EXTERNO
            workOrdersHTML += '</div>' #FIN WO

    
    

    if len(items) > 0 and mode == 1: # Solo si se edita:
    
        workOrdersHTML += '<div class="d-flex justify-content-star flex-shrink-0">'
        workOrdersHTML += '<a class="btn btn-link fs-6" onclick="addWO(' + str(proyect_id) + ')">Add Work Order (+)</a>'
        workOrdersHTML += '</div>'        

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
                
                itemsHTML += '<div class="row">'

                #Codigo item
                itemsHTML += '<div class="col-xl-7 align-items-start">' # style="border:1px solid white; border-width:1px;"

                itemsHTML += '<div class="fs-6 fw-bold mt-3">'
                itemsHTML += '<b>' + code  + '</b>'
                itemsHTML += '</div>'

                itemsHTML += '</div>'


                # #Acciones (cotizar, calendario)
                itemsHTML += '<div class="col-xl-4 align-items-start">' # style="border:1px solid white; border-width:1px;"

                if mode == 1: #edicion

                    if workOrder.state.id >= 2:
                        itemsHTML += '<a class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)">' + workOrder.state.linkDescription + '</a>'

                    # if workOrder.state.id == 3:
                    #     itemsHTML += '<a class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)">Approve quote (+)</a>'

                    # if workOrder.state.id >= 4:
                    #     itemsHTML += '<a class="btn btn-link fs-6" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,0)">Add comment (+)</a>'
                    
                itemsHTML += '</div>'


                # #Acciones (editar, eliminar)
                itemsHTML += '<div class="col-xl-1 text-center">' # style="border:1px solid white; border-width:1px;"

                if mode == 1: #edicion

                    if workOrder.state.id in (1,2,3,4):

                        itemsHTML += '<a href="#" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm me-1" onclick="editItem(' + str(workOrderId) + ',' + str(item.id) + ')"><span class="svg-icon svg-icon-3" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M21.4 8.35303L19.241 10.511L13.485 4.755L15.643 2.59595C16.0248 2.21423 16.5426 1.99988 17.0825 1.99988C17.6224 1.99988 18.1402 2.21423 18.522 2.59595L21.4 5.474C21.7817 5.85581 21.9962 6.37355 21.9962 6.91345C21.9962 7.45335 21.7817 7.97122 21.4 8.35303ZM3.68699 21.932L9.88699 19.865L4.13099 14.109L2.06399 20.309C1.98815 20.5354 1.97703 20.7787 2.03189 21.0111C2.08674 21.2436 2.2054 21.4561 2.37449 21.6248C2.54359 21.7934 2.75641 21.9115 2.989 21.9658C3.22158 22.0201 3.4647 22.0084 3.69099 21.932H3.68699Z" fill="black" /><path d="M5.574 21.3L3.692 21.928C3.46591 22.0032 3.22334 22.0141 2.99144 21.9594C2.75954 21.9046 2.54744 21.7864 2.3789 21.6179C2.21036 21.4495 2.09202 21.2375 2.03711 21.0056C1.9822 20.7737 1.99289 20.5312 2.06799 20.3051L2.696 18.422L5.574 21.3ZM4.13499 14.105L9.891 19.861L19.245 10.507L13.489 4.75098L4.13499 14.105Z" fill="black" /></svg></span></a>'
                        itemsHTML += '<a href="#" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm" onclick="delI(this,' + str(item.id) + ')"><span class="svg-icon svg-icon-3" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" /><path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" /><path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" /></svg></span></a>'

                    if workOrder.state.id == 5:
                        itemsHTML += '<a class="btn btn-link fs-6 " data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrder.id) + ',' + str(item.id) + ',0,1)">Due date (+)</a>'

                itemsHTML += '</div>'

                #Fin fila 1
                itemsHTML += '</div>'


                # Linea azul
                itemsHTML += '<div class="h-3px w-100 bg-primary col-lg-4"></div><br/>'

                                                
                
                # Inicio fila 2
                itemsHTML += '<div class="col-lg-12" style="border:1px solid white; border-width:1px;">'
                                
                itemsHTML += '<div class="row">'
                                
                ##############################################################################################################
                ############################################## Celda (cabecera) ##############################################
                ##############################################################################################################

                place = ''
                if item.place:
                    place = item.place.name


                itemsHTML += '<div class="col-xl-4" style="border:1px solid white; border-width:1px;">'
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

                itemsHTML += '<div class="col-xl-3" style="border:1px solid white; border-width:1px;">'            
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
                
                itemsHTML += '<div class="col-xl-5" style="border:1px solid white; border-width:1px;">'
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
                    itemsHTML += '<div class="d-flex align-items-center collapsible py-3 toggle collapsed mb-0" data-bs-toggle="collapse" data-bs-target="#divItemDetail_' + str(item.id) + '">'
                    itemsHTML += '<div class="btn btn-sm btn-icon mw-20px btn-active-color-primary me-5">'

                    itemsHTML += '<span class="svg-icon toggle-on svg-icon-primary svg-icon-1">'
                    itemsHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
                    itemsHTML += '<rect opacity="0.3" x="2" y="2" width="20" height="20" rx="5" fill="black"></rect>'
                    itemsHTML += '<rect x="6.0104" y="10.9247" width="12" height="2" rx="1" fill="black"></rect>'
                    itemsHTML += '</svg>'
                    itemsHTML += '</span>'

                    itemsHTML += '<span class="svg-icon toggle-off svg-icon-1">'
                    itemsHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
                    itemsHTML += '<rect opacity="0.3" x="2" y="2" width="20" height="20" rx="5" fill="black"></rect>'
                    itemsHTML += '<rect x="10.8891" y="17.8033" width="12" height="2" rx="1" transform="rotate(-90 10.8891 17.8033)" fill="black"></rect>'
                    itemsHTML += '<rect x="6.01041" y="10.9247" width="12" height="2" rx="1" fill="black"></rect>'
                    itemsHTML += '</svg>'
                    itemsHTML += '</span>'
                    
                    itemsHTML += '</div>'

                    itemsHTML += '<h7 class="text-gray-700 cursor-pointer mb-0">See more details</h7>'
                    
                    itemsHTML += '</div>'                     
                                

                    

                    itemsHTML += '<div id="divItemDetail_' + str(item.id) + '" class="row fs-7 ms-1 collapse" style="border:1px solid white; border-width:1px;">'

                    itemsHTML += '<div class="row" style="border:1px solid white; border-width:1px;">'

                    ##############################################################################################################
                    ############################################## Celda (archivos) ##############################################
                    ##############################################################################################################
                  

                    if len(files) > 0 or len(materials) > 0:

                        itemsHTML += '<div class="col-lg-12" style="border:1px solid white; border-width:1px;">'
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


                    itemsHTML += '<div class="row" style="border:1px solid white; border-width:1px;">'

                    ##############################################################################################################
                    ############################################## Celda (imagenes) ##############################################
                    ##############################################################################################################

                    itemsHTML += '<div class="col-lg-12" style="border:1px solid white; border-width:1px;">'                        
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
        itemsHTML += '<div class="col-xl-12 fv-row text-start"><div class="table-responsive">'
        item = Item.objects.get(workorder=workorder, id=itemId)

        if item:
            itemCSs = ItemCommentState.objects.filter(item=item).order_by('-id')  

            if len(itemCSs) > 0:
                itemsHTML += '<div class="separator border-secondary my-10"></div>'
                itemsHTML += '<h7><b>Comments by item:</b></h7>'

    else: 
        itemsHTML += '<div class="col-xl-12 fv-row text-start"><div class="table-responsive">'
        itemCSs = WorkOrderCommentState.objects.filter(workorder=workorder).order_by('-id')

        if len(itemCSs) > 0:
                itemsHTML += '<h7><b>General comments:</b></h7>'

    
    if len(itemCSs) > 0:
        # 27-04-2025
        itemsHTML += '<table class="table table-rounded table-striped"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="15%">State</th><th width="10%">Date</th><th width="10%">Time</th><th width="15%">User</th><th>Notes</th>'

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
            stateName = getStateName(itemCS.state.id, '7')

        user = User.objects.get(id=itemCS.modification_by_user)

        if user:
            username = user.username

        if itemCSF:            
            itemTxt += '<ul class="text-start py-1">'
            
            for file in itemCSF:                    
                itemTxt += '<li><a href=' + file.file.url + ' target="_blank">' + file.name + '</a>'
            
            itemTxt += "</ul>"


        itemsHTML += '<tr class="py-0 fw-bold fs-7 ' + state + '"><td style="padding:0; border:0">' + stateName + '</td><td>' + date + '</td><td>' + time + '</td><td>' + username + '</td><td>' + itemTxt + '</td>'

        user_session = request.user

        if user == user_session and workorder.state == itemCS.state and mode == 1: #edicion
            itemsHTML += '<td><a class="py-0 btn btn-link fs-7" data-bs-toggle="modal" data-bs-target="#modalComment" onclick="loadModal(' + str(workOrderId) + ',' + str(itemId) + ',' + str(itemCS.id) + ',0)">Edit</a></td>'
        else:
             itemsHTML += '<td></td>'
        itemsHTML += '</tr>'
    
    itemsHTML += '</table></div></div>'

    return itemsHTML


#Consulta realizar al crear un proyecto, para obtener todos los proyectos de tal cliente
def getDataCustomer(filtersCustomer, caso):

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


#Funciones Obsoletas
def obs_funct_data_event(filters):
    
    event_data = []

    if filters is None:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(filters)

    # Creamos una lista con los datos de cada proyecto
    for event in events:      
                                
        event_data.append({
            'type_event_id': event.type_event_id,
            'description': event.description,
            'user_id': event.user.id,
            'creation_date': event.creation_date
        })
    
    return event_data


def obs_funct_data_events(proyect_id):
    
    notesHTML = ""
    
    try:

        proyect = Proyect.objects.get(id=proyect_id)
        events = Event.objects.filter(proyect = proyect).order_by('-id')        
       									        
        for event in events:

            event_date = ''

            notesHTML += '<div class="timeline-item">'

            user = User.objects.get(id=event.user)

            try:
                if event.creation_date:
                    event_date = timezone.localtime(event.creation_date)
                    event_date = event_date.strftime('%Y/%m/%d %H:%M:%S')

                if event.type_event_id == 1: #se crea proyecto
                    notesHTML += '<div class="timeline-line w-40px"></div>'
                    notesHTML += '<div class="timeline-icon symbol symbol-circle symbol-40px">'
                    notesHTML += '<div class="symbol-label bg-light">'
                    notesHTML += '<span class="svg-icon svg-icon-2 svg-icon-gray-500">'
                    notesHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'  
                    notesHTML += '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><rect x="0" y="0" width="24" height="24"/><path d="M9.82829464,16.6565893 C7.02541569,15.7427556 5,13.1079084 5,10 C5,6.13400675 8.13400675,3 12,3 C15.8659932,3 19,6.13400675 19,10 C19,13.1079084 16.9745843,15.7427556 14.1717054,16.6565893 L12,21 L9.82829464,16.6565893 Z M12,12 C13.1045695,12 14,11.1045695 14,10 C14,8.8954305 13.1045695,8 12,8 C10.8954305,8 10,8.8954305 10,10 C10,11.1045695 10.8954305,12 12,12 Z" fill="#000000"/></g>'                  
                    notesHTML += '</svg>'
                    notesHTML += '</span>'
                    notesHTML += '</div>'
                    notesHTML += '</div>'

                    notesHTML += timeline_body(event_date, user.first_name + ' ' + user.last_name, user.email, 'Project is created', event.type_event_id)

                if event.type_event_id == 3: #se agrega item
                    notesHTML += '<div class="timeline-line w-40px"></div>'
                    notesHTML += '<div class="timeline-icon symbol symbol-circle symbol-40px">'
                    notesHTML += '<div class="symbol-label bg-light">'
                    notesHTML += '<span class="svg-icon svg-icon-2 svg-icon-gray-500">'
                    notesHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'                    
                    notesHTML += '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><rect x="0" y="0" width="24" height="24"/>'
                    notesHTML += '<path d="M3.5,21 L20.5,21 C21.3284271,21 22,20.3284271 22,19.5 L22,8.5 C22,7.67157288 21.3284271,7 20.5,7 L10,7 L7.43933983,4.43933983 C7.15803526,4.15803526 6.77650439,4 6.37867966,4 L3.5,4 C2.67157288,4 2,4.67157288 2,5.5 L2,19.5 C2,20.3284271 2.67157288,21 3.5,21 Z" fill="#000000" opacity="0.3"/>'
                    notesHTML += '<path d="M8.54301601,14.4923287 L10.6661,14.4923287 L10.6661,16.5 C10.6661,16.7761424 10.8899576,17 11.1661,17 L12.33392,17 C12.6100624,17 12.83392,16.7761424 12.83392,16.5 L12.83392,14.4923287 L14.9570039,14.4923287 C15.2331463,14.4923287 15.4570039,14.2684711 15.4570039,13.9923287 C15.4570039,13.8681299 15.41078,13.7483766 15.3273331,13.6563877 L12.1203391,10.1211145 C11.934804,9.91658739 11.6185961,9.90119131 11.414069,10.0867264 C11.4020553,10.0976245 11.390579,10.1091008 11.3796809,10.1211145 L8.1726869,13.6563877 C7.98715181,13.8609148 8.00254789,14.1771227 8.20707501,14.3626578 C8.29906387,14.4461047 8.41881721,14.4923287 8.54301601,14.4923287 Z" fill="#000000"/>'
                    notesHTML += '</g>'
                    notesHTML += '</svg>'
                    notesHTML += '</span>'
                    notesHTML += '</div>'
                    notesHTML += '</div>'

                    notesHTML += timeline_body(event_date, user.first_name + ' ' + user.last_name, user.email, 'An item has been added', event.type_event_id)

                if event.type_event_id == 4: #se borra item
                    notesHTML += '<div class="timeline-line w-40px"></div>'
                    notesHTML += '<div class="timeline-icon symbol symbol-circle symbol-40px">'
                    notesHTML += '<div class="symbol-label bg-light">'
                    notesHTML += '<span class="svg-icon svg-icon-2 svg-icon-gray-500">'
                    notesHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
                    notesHTML += '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">'
                    notesHTML += '<rect x="0" y="0" width="24" height="24"/>'
                    notesHTML += '<path d="M3.5,21 L20.5,21 C21.3284271,21 22,20.3284271 22,19.5 L22,8.5 C22,7.67157288 21.3284271,7 20.5,7 L10,7 L7.43933983,4.43933983 C7.15803526,4.15803526 6.77650439,4 6.37867966,4 L3.5,4 C2.67157288,4 2,4.67157288 2,5.5 L2,19.5 C2,20.3284271 2.67157288,21 3.5,21 Z" fill="#000000" opacity="0.3"/>'
                    notesHTML += '<path d="M10.5857864,14 L9.17157288,12.5857864 C8.78104858,12.1952621 8.78104858,11.5620972 9.17157288,11.1715729 C9.56209717,10.7810486 10.1952621,10.7810486 10.5857864,11.1715729 L12,12.5857864 L13.4142136,11.1715729 C13.8047379,10.7810486 14.4379028,10.7810486 14.8284271,11.1715729 C15.2189514,11.5620972 15.2189514,12.1952621 14.8284271,12.5857864 L13.4142136,14 L14.8284271,15.4142136 C15.2189514,15.8047379 15.2189514,16.4379028 14.8284271,16.8284271 C14.4379028,17.2189514 13.8047379,17.2189514 13.4142136,16.8284271 L12,15.4142136 L10.5857864,16.8284271 C10.1952621,17.2189514 9.56209717,17.2189514 9.17157288,16.8284271 C8.78104858,16.4379028 8.78104858,15.8047379 9.17157288,15.4142136 L10.5857864,14 Z" fill="#000000"/>'
                    notesHTML += '</g>'                    
                    notesHTML += '</svg>'
                    notesHTML += '</span>'
                    notesHTML += '</div>'
                    notesHTML += '</div>'

                    notesHTML += timeline_body(event_date, user.first_name + ' ' + user.last_name, user.email, 'An item has been deleted', event.type_event_id)


                if event.type_event_id == 6: #se avanza status
                    notesHTML += '<div class="timeline-line w-40px"></div>'
                    notesHTML += '<div class="timeline-icon symbol symbol-circle symbol-40px">'
                    notesHTML += '<div class="symbol-label bg-light">'
                    notesHTML += '<span class="svg-icon svg-icon-2 svg-icon-gray-500">'
                    notesHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
                    notesHTML += '<g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">'
                    notesHTML += '<polygon points="0 0 24 0 24 24 0 24"/>'
                    notesHTML += '<path d="M8.2928955,10.2071068 C7.90237121,9.81658249 7.90237121,9.18341751 8.2928955,8.79289322 C8.6834198,8.40236893 9.31658478,8.40236893 9.70710907,8.79289322 L15.7071091,14.7928932 C16.085688,15.1714722 16.0989336,15.7810586 15.7371564,16.1757246 L10.2371564,22.1757246 C9.86396402,22.5828436 9.23139665,22.6103465 8.82427766,22.2371541 C8.41715867,21.8639617 8.38965574,21.2313944 8.76284815,20.8242754 L13.6158645,15.5300757 L8.2928955,10.2071068 Z" fill="#000000" fill-rule="nonzero" transform="translate(12.000003, 15.500003) scale(-1, 1) rotate(-90.000000) translate(-12.000003, -15.500003) "/>'
                    notesHTML += '<path d="M6.70710678,12.2071104 C6.31658249,12.5976347 5.68341751,12.5976347 5.29289322,12.2071104 C4.90236893,11.8165861 4.90236893,11.1834211 5.29289322,10.7928968 L11.2928932,4.79289682 C11.6714722,4.41431789 12.2810586,4.40107226 12.6757246,4.76284946 L18.6757246,10.2628495 C19.0828436,10.6360419 19.1103465,11.2686092 18.7371541,11.6757282 C18.3639617,12.0828472 17.7313944,12.1103502 17.3242754,11.7371577 L12.0300757,6.88414142 L6.70710678,12.2071104 Z" fill="#000000" fill-rule="nonzero" opacity="0.3" transform="translate(12.000003, 8.500003) scale(-1, 1) rotate(-360.000000) translate(-12.000003, -8.500003) "/>'
                    notesHTML += '</g>'
                    notesHTML += '</svg>'
                    notesHTML += '</span>'
                    notesHTML += '</div>'
                    notesHTML += '</div>'

                    notesHTML += timeline_body(event_date, user.first_name + ' ' + user.last_name, user.email, event.description, event.type_event_id)

            except ValueError:
                messages.error('Server error. Date not exist!')

            notesHTML += '</div>'            
           

    except ValueError:
        messages.error('Server error. Please contact to administrator!')
        
    return notesHTML


###################################
## Funciones para guardar datos ###
###################################

#Instancia para guardar cada evento que ocurre en la WO.
@login_required
def saveEvent(request, type_event_id, proyect, workOrder, item, description):

    # EVENTOS = [
        # (0, 'Other'),
        # (1, 'Create'),
        # (2, 'Update'),
        # (3, 'Delete'),    
    #     ]
    try:

        Event.objects.create(   type_event_id=type_event_id,
                                proyect = proyect,                                    
                                workorder= workOrder, 
                                state = workOrder.state,
                                item = item,
                                description = description,
                                user=request.user.id)
        
    except Proyect.DoesNotExist:        
        messages.error('Server error. Please contact to administrator!')
    

#Instancia para guardar los datos del item.
@login_required
def saveItem(request):    

    if request.method == 'POST':        
        workorder_id = request.POST.get('wo_id')
        item_id = request.POST.get('item_id')

        subcategory_id = request.POST.get('subcategory')
        group_id = request.POST.get('group')
        place_id = request.POST.get('place')
        qty = request.POST.get('qty')
        notes = request.POST.get('notes')
        date_proposed = None

        # Es necesario dar formato a la fecha
        if request.POST.get('date_proposed') != '':
            date_proposed = request.POST.get('date_proposed')
            date_proposed = datetime.strptime(date_proposed, "%m/%d/%Y")

        group = None
        if group_id != '':
            if Group.objects.filter(id=group_id):
                group = Group.objects.get(id=group_id)

        place = None
        if place_id and place_id != '0':
            if Place.objects.get(id=place_id):
                place = Place.objects.get(id=place_id)
        
        if item_id == '':
            item_id = 0

            
        try: 

            workorder = WorkOrder.objects.get(id=workorder_id)
            item = Item.objects.filter(workorder = workorder, id=item_id).first() #No siempre estará, por eso no se usa get

            if item:
                item_id = item.id
                
                item.subcategory = Subcategory.objects.get(id=subcategory_id)
                item.group = group
                item.place = place
                item.qty = qty
                item.notes = notes
                item.date_proposed = date_proposed            
                item.modification_by_user = request.user.id
                item.modification_date = timezone.now()

                item.save()

                saveEvent(request, 2, workorder.proyect, workorder, item, None)

            else:
                item = Item.objects.create( workorder = WorkOrder.objects.get(id=workorder_id),                                            
                                            subcategory = Subcategory.objects.get(id=subcategory_id),
                                            group = group,
                                            place = place,
                                            qty = qty,
                                            notes = notes,
                                            date_proposed = date_proposed,
                                            created_by_user = request.user.id,
                                            modification_by_user = request.user.id)
                item_id = item.id

                saveEvent(request, 1, workorder.proyect, workorder, item, None)


            ################################### Se recorren los atributos ###################################
            
            data = request.POST

            prefijo = "attribute_"
            options = []
            atributtesIds = []


            atributos_permitidos = CategoryAttribute.objects.filter(category=item.subcategory.category).values_list('attribute_id', flat=True)
            item_attributes_permitidos = ItemAttribute.objects.filter(attribute_id__in=atributos_permitidos).values_list('id', flat=True)
            ItemAttribute.objects.filter(item=item).exclude(attribute_id__in=atributos_permitidos).delete()
            ItemAttributeNote.objects.exclude(itemattribute_id__in=item_attributes_permitidos).delete()

            for key, value in data.items():
                if key.startswith(prefijo):
                    try:

                        attribute_id = int(key[len(prefijo):])                                                
                        attribute = Attribute.objects.get(id=attribute_id)

                        item_atributte = ItemAttribute.objects.filter(item = item, attribute = attribute).first()

                        if item_atributte:

                            item_atributte.notes = value

                            if value.strip() != '':
                                atributtesIds.append(attribute_id) # Se considera solo si tiene valor
                                item_atributte.save()                                                    
                        else:

                            if value.strip() != '':
                                atributtesIds.append(attribute_id) # Se considera solo si tiene valor
                                item_atributte = ItemAttribute.objects.create(   item = item,
                                                                                attribute = attribute,
                                                                                notes = value)

                        if attribute.multiple:                                     
                            options = request.POST.getlist(key)

                            ItemAttributeNote.objects.filter(itemattribute=item_atributte).exclude(attributeoption__id__in = options).delete()

                            for option in options:
                                
                                if option != '':

                                    atributtesIds.append(attribute_id) # Se considera solo si tiene valor
                                                                        
                                    item_atributte_option = ItemAttributeNote.objects.filter(itemattribute = item_atributte, attributeoption = AttributeOption.objects.get(id= option)).first()

                                    if not item_atributte_option:                                        
                                        ItemAttributeNote.objects.create(   itemattribute = item_atributte,
                                                                            attributeoption = AttributeOption.objects.get(id= option))
                                        

                            

                    except ValueError:
                        messages.error(request, 'Server error. Please contact to administrator!')

            
            ItemAttribute.objects.filter(item=item).exclude(attribute__in=Attribute.objects.filter(id__in=atributtesIds)).delete() # Debe filtrar por el item!!! y luego excluir

            ################################### Se recorren los materiales ###################################

            materials = request.POST.getlist('material[]')
            materialsIds = request.POST.getlist('materialIds[]')
            materialsQTY = request.POST.getlist('materialQTY[]')
            materialsF = request.FILES.getlist('materialFile[]')
            materialsFileOK = request.POST.getlist('materialFileOk[]')            
            indexFile = 0
            

            for index, material in enumerate(materials):                
                file = None
                fileName = None
                qty = ""
                id = "0"

                if material.strip() != "":                    
                    try:
                        
                        if int(materialsFileOK[index]) == 1:
                            file = materialsF[indexFile]
                            indexFile += 1
                            fileName = file.name
                        
                        if file:
                            if validateTypeFile(file.content_type):
                                pass
                            else:
                                file = None
                                name = ''

                        if materialsQTY[index]:
                            qty = materialsQTY[index]

                        
                        if materialsIds[index]:
                            if materialsIds[index] != '0':
                                id = materialsIds[index].split('_')[1] 

                        item_material = ItemMaterial.objects.filter(item = item, id = id).first()

                        if item_material:                            
                            
                            item_material.qty = qty
                            item_material.notes = material

                            if file:

                                item_material.file = file
                                item_material.name = fileName

                            item_material.save()                                                
                        
                        else:

                            ItemMaterial.objects.create(    item = item,
                                                            file = file,
                                                            name = fileName,
                                                            qty = qty,
                                                            notes = material)

                    except OSError: #Guardarlo como archivo adjunto

                        item_material = ItemMaterial.objects.filter(item = item, id = id).first()

                        if item_material:

                            # item_material.file = file
                            # item_material.name = fileName
                            item_material.qty = qty
                            item_material.notes = material

                            item_material.save()
                        
                        else:
                        
                            ItemMaterial.objects.create(   item = item,
                                                            file = None,
                                                            name = '',
                                                            qty = qty,
                                                            notes = material)
                            
                    except:
                        messages.error(request, 'Text images not found!')

            
            ################################### Se recorren las imagenes ###################################

            images = request.POST.getlist('image[]')
            imagesIds = request.POST.getlist('imageIds[]')
            imagesF = request.FILES.getlist('imageFile[]')
            imagesFileOk = request.POST.getlist('imageFileOk[]')            
            indexFile = 0
            

            for index, imageId in enumerate(imagesIds):                
                file = None
                fileName = None
                notes = None
                id = '0'
                pre = ''

                if int(imagesFileOk[index]) == 1 or imageId != '0':

                    try:

                        if imagesIds[index]:
                            if imagesIds[index] != '0':
                                pre = imagesIds[index].split('_')[0] 
                                id = imagesIds[index].split('_')[1] 

                        notes = images[index]
                        
                        if int(imagesFileOk[index]) == 1:                        
                            file = imagesF[indexFile]
                            fileName = file.name
                            indexFile += 1

                            if validateTypeFile(file.content_type):
                                # Abrir la imagen usando PIL
                                imagen = Image.open(file)  


                        if pre == 'FIL' and id != '0':
                            ItemFile.objects.filter(item = item, id = id).delete()
                            id = '0'

                                                                                                                                                                                             
                        if pre == 'IMG' or id == '0':

                            item_image = ItemImage.objects.filter(item = item, id = id).first()
                            
                            if item_image:
                                item_image.notes = notes

                                if file:
                                    item_image.file = file
                                    item_image.name = fileName

                                item_image.save()
                            else:

                                ItemImage.objects.create(   item = item,
                                                            file = file,
                                                            name = fileName,
                                                            notes = notes)
                                                       
                    except OSError: #Guardarlo como archivo adjunto

                        if pre == 'FIL' or id == '0':

                            item_file = ItemFile.objects.filter(item = item, id = id).first()
                                
                            if item_file:
                                item_file.notes = notes
                                
                                if file:
                                    item_file.file = file
                                    item_file.name = fileName

                                item_file.save()
                        
                            else:
                                ItemFile.objects.create(  item = item,
                                                        file = file,
                                                        name = fileName,
                                                        notes = notes)

                    except:
                        messages.error(request, 'Text images not found!')


        except ValueError:
            messages.error(request, 'Server error. Please contact to administrator!')


    return JsonResponse({'result': item_id})


#Instancia para guardar los comentarios, genéricos o particulaes.
@login_required
def saveComment(request):
    
    if request.method == 'POST':
        workOrderId = request.POST.get('id1')
        itemId = request.POST.get('id2')
        commentId = request.POST.get('id3')
        notes = request.POST.get('notes')
        date_end = request.POST.get('date_end')
        responsible_id = request.POST.get('responsable')        

        workorder = WorkOrder.objects.get(id=workOrderId)
        item = Item.objects.filter(workorder = workorder, id=itemId).first() #No siempre estará, por eso no se usa get

        #A nivel de item       
        if item: 
            
            #Si el comentarioId existe, entonces se edita. En caso contrario, se crea.
            item_coment_save = ItemCommentState.objects.filter(id=commentId, item=item, state=workorder.state).first()

            if item_coment_save:
                item_coment_save.notes = notes
                item_coment_save.modification_by_user = request.user.id
                item_coment_save.save()

            else:                                    
                item_coment_save = ItemCommentState.objects.create( item = item,
                                                                    state = workorder.state,
                                                                    notes = notes,
                                                                    created_by_user = request.user.id,
                                                                    modification_by_user = request.user.id)
                                       
            ################################### Se recorren los archivos ###################################

            files = request.FILES.getlist('files[]')

            for file in files:
                    
                if validateTypeFile(file.content_type):
                    try:
                            
                        ItemCommentStateFile.objects.create(item_comment_state = item_coment_save,
                                                            file = file,
                                                            name = file.name)
                    except:                
                        messages.error(request, 'Server error. Please contact to administrator!')
                        return JsonResponse({'result': "Server error. Please contact to administrator."})
                                        
            return JsonResponse({'result': "OK"})


        else:

            #Comentario genérico
            if int(itemId) == 0:


                #Si el comentarioId generico existe, entonces se edita. En caso contrario, se crea.
                item_coment_save = WorkOrderCommentState.objects.filter(id=commentId, state=workorder.state).first()

                if item_coment_save:
                    item_coment_save.notes = notes
                    item_coment_save.modification_by_user = request.user.id
                    item_coment_save.save()

                else:                                    
                        
                    item_coment_save = WorkOrderCommentState.objects.create(workorder = workorder,
                                                                            state = workorder.state,
                                                                            notes = notes,
                                                                            created_by_user = request.user.id,
                                                                            modification_by_user = request.user.id)
                            
                ################################### Se recorren los archivos ###################################

                files = request.FILES.getlist('files[]')

                for file in files:
                       
                    if validateTypeFile(file.content_type):
                        try:
                                
                            WorkOrderCommentStateFile.objects.create(   workorder_comment_state = item_coment_save,
                                                                        file = file,
                                                                        name = file.name)
                        except:                
                            messages.error(request, 'Server error. Please contact to administrator!')
                            return JsonResponse({'result': "Server error. Please contact to administrator."})
                            
                return JsonResponse({'result': "OK"})
                            
            else:

                messages.error(request, 'Server error. Please contact to administrator!')
                return JsonResponse({'result': "Server error. Please contact to administrator."})


#Instancia para guardar los comentarios, genéricos o particulaes.
@login_required
def saveCalendar(request):

    if request.method == 'POST':
        workOrderId = request.POST.get('id1')
        itemId = request.POST.get('id2')
        taskId = request.POST.get('id3')
        #commentId = request.POST.get('id3')        
        dateStart_get = request.POST.get('dateA')
        dateStartHour_get = request.POST.get('dateA2')        
        dateEnd_get = request.POST.get('dateB')
        dateEndHour_get = request.POST.get('dateB2')
        checkAllDay = request.POST.get('checkAllDay')
        
        responsible_id = request.POST.get('responsible')
        statusDate = request.POST.get('statusDate')

        #No siempre estará, por eso no se usa get
        workorder = WorkOrder.objects.filter(id=workOrderId).first()
        item = Item.objects.filter(workorder = workorder, id=itemId).first() 
        
        responsible = Responsible.objects.filter(id=responsible_id).first()
                
        if dateStart_get != '' and dateStart_get is not None:
            # Es necesario dar formato a la fecha
            
            if dateEnd_get == '' or dateEnd_get is None:
                dateEnd_get = dateStart_get

            if dateStartHour_get == '' or dateStartHour_get == None:
                dateStartHour_get = '12:00 AM' 

            if dateEndHour_get == '' or dateEndHour_get == None:
                dateEndHour_get = '11:59 PM' 

            if checkAllDay:
                dateStart_get += ' 12:00 AM'
                dateEnd_get += ' 11:59 PM'
                checkAllDay = True
            else:
                dateStart_get += ' ' + dateStartHour_get
                dateEnd_get += ' ' + dateEndHour_get
                checkAllDay = False
            
            dateStart = datetime.strptime(dateStart_get, "%m/%d/%Y %I:%M %p")
            dateEnd = datetime.strptime(dateEnd_get, "%m/%d/%Y %I:%M %p")

        else:
            dateStart = None
            dateEnd = None


        calendar = None

        #A nivel de item       
        if item:
            calendar = CalendarItem.objects.filter(item = item).first()
        #A nivel de work order 
        elif workorder:
            calendar = CalendarWorkOrder.objects.filter(workorder = workorder).first()
                    
                        
        if calendar:

            try:

                calendar.date_start = dateStart
                calendar.date_end = dateEnd
                calendar.allday = checkAllDay
                calendar.responsible = responsible
                calendar.modification_by_user = request.user.id
                calendar.modification_date = datetime.now()

                if statusDate:
                    calendar.status = statusDate

                calendar.save()

                saveCalendarItems(request)
                saveCalendarComments(request, calendar, item, workorder)

                return JsonResponse({'result': "OK"})
            
            except:

                messages.error(request, 'Server error. Please contact to administrator!')
                return JsonResponse({'result': "Server error. Please contact to administrator."})


        elif workorder or item:

            try:
                
                if item:
                    calendar_create = CalendarItem.objects.create(  item = item,
                                                                    date_start = dateStart,
                                                                    date_end = dateEnd,
                                                                    allday = checkAllDay,
                                                                    responsible = responsible,
                                                                    created_by_user = request.user.id,
                                                                    modification_by_user = request.user.id)
                    
                    saveCalendarComments(request, calendar_create, item, workorder)
                    
                    return JsonResponse({'result': "OK"})

                elif workorder:
                    
                    calendar_create = CalendarWorkOrder.objects.create( workorder = workorder,
                                                                        date_start = dateStart,
                                                                        date_end = dateEnd,
                                                                        allday = checkAllDay,
                                                                        responsible = responsible,
                                                                        created_by_user = request.user.id,
                                                                        modification_by_user = request.user.id)
                    
                    saveCalendarItems(request)
                    saveCalendarComments(request, calendar_create, item, workorder)                

                    return JsonResponse({'result': "OK"})
                
                else:
                    
                    messages.error(request, 'Server error. Please contact to administrator!')
                    return JsonResponse({'result': "Server error. Please contact to administrator."})
            
            except:

                messages.error(request, 'Server error. Please contact to administrator!')
                return JsonResponse({'result': "Server error. Please contact to administrator."})
            

        elif workorder is None and item is None:

            try:
                
                calendar = CalendarTask.objects.filter(id = taskId).first()

                if calendar:
                    
                    calendar.date_start = dateStart
                    calendar.date_end = dateEnd
                    calendar.allday = checkAllDay
                    calendar.responsible = responsible
                    calendar.modification_by_user = request.user.id
                    calendar.modification_date = datetime.now()

                    if statusDate:
                        calendar.status = statusDate

                    calendar.save()

                else:

                    calendar = CalendarTask.objects.create( date_start = dateStart,
                                                            date_end = dateEnd,
                                                            allday = checkAllDay,
                                                            responsible = responsible,
                                                            created_by_user = request.user.id,
                                                            modification_by_user = request.user.id)

                    #saveCalendarItems(request)
                saveCalendarComments(request, calendar, None, None)

                return JsonResponse({'result': "OK"})
            

            except:

                messages.error(request, 'Server error. Please contact to administrator!')
                return JsonResponse({'result': "Server error. Please contact to administrator."})
         
            
#Instancia para cambiar estado del item
@login_required
def saveQuote(request):

    # itemId = request.POST.get('i')        
    # checked = request.POST.get('t')
    # status = 1
    
    # if checked == 'true':
    #     status = 2

    # item = Item.objects.get(id=itemId)
    # item.status = status
    # item.modification_by_user = request.user.id
    # item.modification_date = datetime.now()
    # item.save()

    # return JsonResponse({'result': "OK"})


    data = request.POST

    txtQuote_ = "txtQuote_"        
                        
    try:
        
        for key, value in data.items():
            if key.startswith(txtQuote_) and value.strip() != "":

                item_id = int(key[len(txtQuote_):])
                item = Item.objects.get(id=item_id)

                if item.quote != value.strip():
                    item.quote = value.strip()
                    item.save()
                            
        return JsonResponse({'result': "OK"})

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
        return JsonResponse({'result': "Error"})


#Instancia para guardar los datos del material
@login_required
def saveMaterial(request):


    data = request.POST

    dateR = "dateR_"
    qtyR = "qtyR_"        
                        
    try:
        
        for key, value in data.items():
            if key.startswith(dateR):  #and value.strip() != "":

                material_id = int(key[len(dateR):])
                material = ItemMaterial.objects.get(id=material_id)

                if material.date_received != value.strip():
                    material.date_received = value.strip()
                    material.save()

            if key.startswith(qtyR): #and value.strip() != "":

                material_id = int(key[len(qtyR):])
                material = ItemMaterial.objects.get(id=material_id)

                if material.qty_received != value.strip():
                    material.qty_received = value.strip()
                    material.save()
                
        return JsonResponse({'result': "OK"})

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
        return JsonResponse({'result': "Error"})


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
                dateStartHour_get = '12:00 AM' 

            if dateEndHour_get == '' or dateEndHour_get == None:
                dateEndHour_get = '11:59 PM' 

            if checkAllDay and checkAllDay == '1':
                dateStart_get += ' 12:00 AM'
                dateEnd_get += ' 11:59 PM'
                checkAllDay = True
            else:
                dateStart_get += ' ' + dateStartHour_get
                dateEnd_get += ' ' + dateEndHour_get
                checkAllDay = False
            
            dateStart = datetime.strptime(dateStart_get, "%m/%d/%Y %I:%M %p")
            dateEnd = datetime.strptime(dateEnd_get, "%m/%d/%Y %I:%M %p")

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


#Instancia para guardar notas WO
@login_required
def saveWO(request):

    woId = request.POST.get('woId')
    notes = request.POST.get('notes')
                            
    try:
        
        wo = WorkOrder.objects.filter(id=woId).first()
        wo.description = notes
        wo.save()
                            
        return JsonResponse({'result': "OK"})

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
        return JsonResponse({'result': "Error"})





##################################
## Funciones para borrar datos ###
##################################

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

    try:
        proyect = Proyect.objects.get(id = proyect_id)
        saveEvent(request, 3, proyect, None, None, 'Address : ' + proyect.customer.address)
        proyect.delete()
        status = 1

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


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

##################################
## Funciones para editar datos ###
##################################

#Funcion utilizada para avanzar de estado/etapa
@login_required
def updateStatus(request):
    workOrderId = request.POST.get('w') 
    status = 0

    try:
        workOrder = WorkOrder.objects.get(id = workOrderId)
        workOrder.state = State.objects.get(id = (workOrder.state.id + 1))
        workOrder.save()


        try: 
            if 'stateId' in request.session:
                request.session['stateId'] = workOrder.state.id                
        except:
            None


        description = "Change to status: " + workOrder.state.name

        saveEvent(request, 2, workOrder.proyect, workOrder, None, description)

        
        status = 1

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


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
                files = ItemCommentStateFile.objects.filter(item_comment_state = itemCS)

    #General
    else:

        itemCS = WorkOrderCommentState.objects.filter(id=commentId, workorder=workorder).first() 

        if itemCS:
            itemCSId = str(itemCS.id)
            itemTxt = itemCS.notes
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
    
    
    itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3">' + modalSubTitle + '</div>'
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
    style_display = ''
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
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="40%">Responsible</th><th width="10%">' + htmlSpanCalendar() + 'Date</th><th width="20%">Status</th><th width="20%"></th></tr></thead><tbody>'
        else:
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="30%">Responsible</th><th width="40%">' + htmlSpanCalendar() + 'Date</th><th width="20%">Status</th><th width="0%"></th></tr></thead><tbody>'
        
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
            itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
            itemsHTML += '</td><td>'
            itemsHTML += '-'        
            itemsHTML += '</td><td>'
            itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
            itemsHTML += '</td><td>'
            itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
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

        itemsHTML += '<div class="col-md-12">'
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
                style_display = '; display:none'

            if calendar.responsible:
                responsibleId = calendar.responsible.id

            if calendar.status:
                status = calendar.status

        itemsHTML += '<form id="formItem_0" method="POST" enctype="multipart/form-data">' # Aca el itemId = 0
    
        # Work order
        
        itemsHTML += '<b style="margin-left:-10px">Work Order:</b>'
        itemsHTML += '<div class="row"><div class="table-responsive">' 
                        
        itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="5%">N°</th><th width="30%">Responsible</th><th width="40%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'
        
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
        itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '-'        
        itemsHTML += '</td><td>'
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
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
            itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="10%">Code</th><th width="30%">Responsible</th><th width="35%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'

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
                style_display = ''
                
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
                            style_display = '; display:none'

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
                    itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateItemA2[]" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
                    itemsHTML += '</td><td>'
                    itemsHTML += '-'        
                    itemsHTML += '</td><td>'
                    itemsHTML += '<input class="form-control form-control-solid date-picker py-2" name="dateItemB[]" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
                    itemsHTML += '</td><td>'
                    itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateItemB2[]" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
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

        itemsHTML += '<div class="col-md-12">'
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
                style_display = '; display:none'

            if calendar.responsible:
                responsibleId = calendar.responsible.id

            if calendar.status:
                status = calendar.status

        itemsHTML += '<form id="formTask_' + str(id) + '" method="POST" enctype="multipart/form-data">'


        itemsHTML += '<div class="row">' 
                        
        itemsHTML += '<table class="table table-bordered"><thead><tr class="fw-bolder fs-7 text border-bottom border-gray-200 py-4"><th width="35%">Responsible</th><th width="40%">' + htmlSpanCalendar() + 'Date</th><th width="15%">Status</th></tr></thead><tbody>'
        
        itemsHTML += '<tr><td>'
        itemsHTML += '<select class="form-select form-select-sm form-select-solid selectResponsible" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="false" name="responsible">'
        itemsHTML += htmlResponsibleSelect(responsibleId)
        itemsHTML += '</select>'
        itemsHTML += '</td><td>'
        
        # Date Start - End
        
        itemsHTML += '<table><tr><td>'
        
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateA" name="dateA" placeholder="Start" value="' + fecha_inicio + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateA2" placeholder="Time" value="' + fechaDate_inicio + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '-'        
        itemsHTML += '</td><td>'
        itemsHTML += '<input class="form-control form-control-solid date-picker py-2" id="dateB" name="dateB" placeholder="End" value="' + fecha_fin + '" style="max-width: 90px"/>'
        itemsHTML += '</td><td>'
        itemsHTML += '<input type="time" class="form-control form-control-solid hour-picker py-2" name="dateB2" placeholder="Time" value="' + fechaDate_fin + '" style="max-width: 80px'+ style_display +'"/>'
        itemsHTML += '</td><td>'

        itemsHTML += '<tr><td class="p-3 text-start" colspan=5>'

        if allDay:
            itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem" checked>'
        else:
            itemsHTML += '<input class="form-check-input checkAllDay" name="checkAllDay" type="checkbox" value="1" style="width:1.3rem; height:1.3rem">'
        
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

        itemsHTML += '<div class="col-md-12">'
        itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveCalendar(0,0,' + str(id) + ')">Save</button>'
        itemsHTML += '</div>'                            
        
        itemsHTML += '</div>'
        
        # itemsHTML += '<script>$("#modalCommentDelete").hide(); $("#divModalDialog").removeClass("mw-650px").addClass("mw-900px"); </script>'

        itemsHTML += '</form>'
        
            
    itemsHTML += '</div>'    

    return itemsHTML






##################################
## Funciones para validar ###
##################################

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


##################################
## Funciones varias ###
##################################

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
def getStateName(stateId, fs):
    
    state = State.objects.get(id = stateId)

    name = state.name
    description = state.description

    stateHTML = ''

    #stateHTML += '<i class="fas fa-question-circle" data-bs-toggle="tooltip" title="' + description + '"></i>'

    if fs != "":
        stateHTML += '<div class="fs-' + fs + ' fw-bold p-2 badge-state-' + str(stateId) + '">'
        stateHTML += name
        stateHTML += '</div>'
    else:
        stateHTML += '<th style="width: 90px; max-width: 90px; padding: 0;"><div class="badge-state-' + str(stateId) + ' p-1" style="width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 10px; text-align: center;" title="' + name + '" >'
        stateHTML += name
        stateHTML += '</div></th>'

    return stateHTML																									

from collections import defaultdict
#Retorna resumen WO´s
def getResumenWOs(request, proyect):

    state = None

    try: 
        if 'stateId' in request.session:
            state = State.objects.filter(id = request.session['stateId']).first()         
    except:
        None

    if state:
        wos = WorkOrder.objects.filter(proyect = proyect, status=1, state = state)
    else:
        wos = WorkOrder.objects.filter(proyect = proyect, status=1)

    # Obtener eventos relevantes
    eventos = Event.objects.filter(type_event_id=2, workorder__in = wos, item = None).select_related('workorder', 'state')
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
            fecha_str = fecha.strftime("%b %d, %Y") if fecha else ''
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

        saveEvent(request, 2, proyect, workorder, None, 'Create WO')

        return workorder
        
    except:
        return None


def timeline_body(date_str, name, email, description, stateId):
    
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




import io
def generate_pdf(request, workorderId):
    try:
        wo = WorkOrder.objects.get(id=workorderId)
    except Proyect.DoesNotExist:
        raise Http404("El proyecto no existe")
    
    htmlCabecera = ""
    
    if wo:

        #Cabecera cliente

        htmlCabecera += "<table class='table_wo'>"
        
        address = ''

        if wo.proyect.customer.address != "":
            address += wo.proyect.customer.address

        if wo.proyect.customer.apartment != "":
            address += "," + wo.proyect.customer.apartment

        if wo.proyect.customer.city != "":
            address += "," + wo.proyect.customer.city

        if wo.proyect.customer.state != "":
            address += "," + wo.proyect.customer.state

        if wo.proyect.customer.zipcode != "":
            address += "," + wo.proyect.customer.zipcode
        
        name = wo.proyect.customer.name if str(wo.proyect.customer.name) != "" else "--"
        phone = wo.proyect.customer.phone if str(wo.proyect.customer.phone) != "" else "--"
        email = wo.proyect.customer.email if str(wo.proyect.customer.email) != "" else "--"

        code = wo.proyect.code if str(wo.proyect.code) != "" else "--"
        
        
        htmlCabecera += "<tr><th colspan=2></th><th></th><th>Code:</th><td>" + str(code) + "</td></tr>"
        htmlCabecera += "<tr><th style='width: 88px'>Address:</th><td style='width: 340px'>" + address + "</td><th></th><th style='width: 80px'>Phone:</th><td style='width: 250px'>" + str(phone) + "</td></tr>"
        htmlCabecera += "<tr><th>Customer:</th><td>" + str(name) + "</td><th></th><th>Email:</th><td>" + str(email) + "</td></tr>"        
        
        htmlCabecera += "</table>"
        
                
        #Cabecera proyecto
        htmlCabecera += "<table class='table_wo'>"

        

        decorators = ProyectDecorator.objects.filter(proyects = wo.proyect)

        if decorators:

            htmlCabecera += "<tr><th rowspan='" + str(len(decorators)) + "' style='width: 85px; text-align: left; vertical-align: top;'>Decorator:</th>"
            n = 0

            for decorator in decorators:
                name = decorator.name if str(decorator.name) != "" else "--"
                phone = decorator.phone if str(decorator.phone) != "" else "--"
                email = decorator.email if str(decorator.email) != "" else "--"

                if n == 0:
                    htmlCabecera += "<td>" + str(name) + " / " + str(phone) + " / " + str(email) + "</td>"
                    htmlCabecera += "</tr>"
                    n+=1
                else:
                    htmlCabecera += "<tr><td>" + str(name) + " / " + str(phone) + " / " + str(email) + "</td></tr>"            

        htmlCabecera += "</table>"

        #Items


        #Cabecera proyecto

        items = Item.objects.filter(workorder = wo).order_by("id")                        
                
        if items:
            
            n = 1
            
            for item in items:

                #htmlCabecera += " <div class='new-page'><table class='table_item'>"
                htmlCabecera += "<div><table class='table_item'>"
                htmlCabecera += "<tr><th colspan='2' style='background-color:#f1f1f1; border:1px solid'>Item: " + str(code) + "-" + str(n) + "</th></tr>"
                htmlCabecera += "</table></div>"


                n+=1

                category = item.subcategory.category.name if str(item.subcategory.category.name) != "" else "--"
                
                subcategory = "--"
                if item.subcategory.name:
                    subcategory = item.subcategory.name if str(item.subcategory.name) != "" else "--"
                
                group = "--"
                if item.group:
                    group = item.group.name if str(item.group.name) != "" else "--"
                
                place = "--"
                if item.place:
                    place = item.place.name if str(item.place.name) != "" else "--"
                
                
                qty = item.qty if str(item.qty) != "" else "--"

                
                
                
                date_end = "--"
                responsible = " "


                calendar = CalendarItem.objects.filter(item = item).first()

                if calendar:

                    if calendar.responsible:
                        responsible = calendar.responsible.name

                    if calendar.date_start:
                        if calendar.allday:
                            date_end = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y')
                        else:
                            date_end = timezone.localtime(calendar.date_start).strftime('%m/%d/%Y %I:%M %p')

                notes = item.notes if str(item.notes) != "" else "--"


                htmlCabecera1 = "<table class='table_item_detalle'>"
                htmlCabecera1 += "<tr><th align='center' colspan=6><h1>" + str(category) + "</h1></th></tr>"
                htmlCabecera1 += "<tr><th>Sub Category:</td><td>" + str(subcategory) + "</td><th>Group:</td><td>" + str(group) + "</td><th>Place:</td><td>" + str(place) + "</td></tr>"
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                htmlCabecera1 += "<tr><th>QTY:</td><td>" + str(qty) + "</td><th>Due date:</th><td>" + str(date_end) + "</td><th>Responsible:</th><td>" + str(responsible) + "</td></tr>"                
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                htmlCabecera1 += "<tr><th style='vertical-align: top;'>Notes:</th><td colspan=3>" + str(notes) + "</td></tr>"
                htmlCabecera1 += "<tr style='height:5px'><th></th></tr>"
                

                attributes = ItemAttribute.objects.filter(item = item)
                # htmlCabecera2 = ""
                atributos1 = ''
                atributos2 = ''

                if attributes:
                    # htmlCabecera2 = "<table class='table_item_detalle'>"

                    for attribute in attributes:
                                                
                        atributteOptions = ItemAttributeNote.objects.filter(itemattribute = attribute)

                        if atributteOptions:
                            
                            name = attribute.attribute.name if str(attribute.attribute.name) != "" else "--"
                            atributos2 += "<tr><th valign='top'>" + str(name) + ":</th><td colspan=5>"
                            atributos2 += "<table class='tabla_atributo_opciones'>"
                            atributos2 += "<tr>"

                            tds = 0

                            for option in atributteOptions:
                                tds += 1
                                notes = option.attributeoption.name if str(option.attributeoption.name) != "" else "--"
                                atributos2 += "<td valign='middle'>" + str(notes) + "</td><td>"
                                
                                if option.attributeoption.file:
                                    atributos2 += "<img src='media/" + str(option.attributeoption.file.name) + "'width='80%'/>"
                                
                                atributos2 += '</td>'


                                if tds == 2:
                                    tds = 0
                                    atributos2 += "</tr><tr>"

                            atributos2 += "</tr></table>"
                            atributos2 += "</td></tr>"


                        else:                            

                            name = attribute.attribute.name if str(attribute.attribute.name) != "" else "--"
                            notes = attribute.notes if str(attribute.notes) != "" else "--"
                            atributos1 += "<tr><th>" + str(name) + ":</th><td colspan=3>" + str(notes) + "</td></tr>"
                            atributos1 += "<tr style='height:5px'><th></th></tr>"                            

                                    
                    htmlCabecera1 += atributos1 + atributos2
                    
                    # htmlCabecera2 += "</table>"


                # htmlCabecera += "<tr><th style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera1 + "</th><th style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera2 + "</th></tr>"

                htmlCabecera1 += "</table>"
                htmlCabecera += htmlCabecera1

            
                materials= ItemMaterial.objects.filter(item = item).order_by('id')

                htmlCabeceraMat = ""
                htmlCabeceraImg = ""

                if materials:
                    
                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td colspan='3' style='background-color:#f1f1f1'><b>Materials:</b></td></tr>"                    
                    table_img = ""
                    nt = 1

                    htmlCabeceraMat += "<table><tr><td style='width:300px; border-left:none; border-top:none'></td><td style='width:170px'>QTY</td><td style='width:170px'>Received QTY</td><td style='width:100px'>Received Date</td></tr>"
                    
                    for material in materials:

                        materialName = str(material.notes)
                        qty = str(material.qty)   
                        qtyR = ''             
                        dateR = ''

                        if material.qty_received:
                            qtyR = material.qty_received

                        if material.date_received:                            
                            dateR = material.date_received

                        htmlCabeceraMat += '<tr><td>' + materialName + '</td>' 
                        htmlCabeceraMat += '<td>' + qty + '</td>' 
                        htmlCabeceraMat += '<td>' + qtyR + '</td>'
                        htmlCabeceraMat += '<td>' + dateR + '</td>'

                        htmlCabeceraMat += '</tr>'
                    
                    htmlCabeceraMat += "</table><br/>"                     
                    htmlCabecera += htmlCabeceraMat
                    
                
                    
                    for material in materials:
                        file = material.file.name if str(material.file.name) != "" else "--"
                        notes = material.notes if str(material.notes) != "" else "--"
                        
                        table_img = "<table><tr><td style='padding:0 0; text-align: center; vertical-align: top; height=180px'><img src='media/" + file + "'width='90%'/></td></tr><tr><td style='text-align: left; vertical-align: top;'>" + notes + "</td></tr></table>"                                                
                        
                        if material.file:
                            if material.file.url[-4:] not in ('.pdf','.doc','.xls','.ppt') and material.file.url[-5:] not in ('.docx','.xlsx','.pptx'):
                                if nt == 1:
                                    htmlCabeceraImg += "<tr><td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                                elif nt == 2:
                                    htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                                elif nt == 3:
                                    htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td></tr>"
                                    nt = 0
                            
                                nt += 1
                    
                    htmlCabecera += htmlCabeceraImg

                    htmlCabecera += "</table>"


                images= ItemImage.objects.filter(item = item)

                if images:
                    
                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td colspan='3' style='background-color:#f1f1f1'><b>Images:</b></td></tr>"
                    htmlCabeceraImg = ""
                    table_img = ""
                    nt = 1
                    for image in images:
                        file = image.file.name if str(image.file.name) != "" else "--"
                        notes = image.notes if str(image.notes) != "" else "--"
                        table_img = "<table><tr><td style='padding:0 0; text-align: center; vertical-align: top; height=180px'><img src='media/" + file + "'width='90%'/></td></tr><tr><td style='text-align: left; vertical-align: top;'>" + notes + "</td></tr></table>"                                                
                        if nt == 1:
                            htmlCabeceraImg += "<tr><td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                        elif nt == 2:
                            htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td>"
                        elif nt == 3:
                            htmlCabeceraImg += "<td style='padding:0 0; text-align: left; vertical-align: top;'>" + table_img + "</td></tr>"
                            nt = 0
                        
                        nt += 1
                    
                    htmlCabecera += htmlCabeceraImg

                    htmlCabecera += "</table>"



                if wo.description and wo.description.strip() != '':

                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td style='background-color:#f1f1f1'><b>Notes:</b></td></tr>"
                    htmlCabecera += "<tr><td>" + wo.description + "</td></tr>"
                    htmlCabecera += "</table>"
            


                



    template = get_template('proyect/pdf_template.html')
    context = {
        'CABECERA': htmlCabecera,
        'URL': settings.BASE_DIR,
        # 'MEDIA_URL': settings.MEDIA_URL
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="WorkOrder_{}.pdf"'.format(workorderId)

    pisa_status = pisa.CreatePDF(io.StringIO(html), 
                    dest=response,
                    link_callback=link_callback) 

    if pisa_status.err:
        return HttpResponse('Error generando el PDF', status=500)
    
    return response


from django.conf import settings
from django.contrib.staticfiles import finders
import os

def link_callback(uri, rel):
    """
    Convierte URIs en rutas absolutas para xhtml2pdf
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # por ejemplo: /static/
        sRoot = settings.STATIC_ROOT      # por ejemplo: /var/www/static/
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # deja la URI como está si no se puede procesar

    if not os.path.isfile(path):
        raise Exception('Archivo no encontrado: %s' % path)
    return path