from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib import messages
from datetime import datetime # dar formato a la fecha
from django.shortcuts import redirect # redireccionar a páginas
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q # permite realizar consultas complejas
from django.urls import reverse #evita doble envio de formulario

# from django.core.files.storage import FileSystemStorage #para las imagenes

from PIL import Image #Para validar el tipo de imagen
from django.core.exceptions import ValidationError #Para manejar excepciones

from django.utils import timezone #Para ver la hora correctamente.

from xhtml2pdf import pisa #Para el PDF
from django.template.loader import get_template #Para el PDF
from django.http import Http404 #Para el PDF
from django.conf import settings #Para el PDF, manejar las rutas

from django.contrib.auth.models import User #Datos del usuario
from .models import Type, Responsible, Customer, State, Proyect, Decorator, Event, Category, Subcategory, Place, Category_Attribute, Attribute, Item, Item_Attribute, Item_Images, Group, Item_Files, Item_Comment_State, Item_Comment_State_Files #Aquí importamos a los modelos que necesitamos

@login_required
def panel_view(request):

    #Consulta los proyectos/tipos/estados desde la base de datos    
    types = Type.objects.filter(status=1).order_by('id')
    states = State.objects.filter(status=1).order_by('id')

    type_id = 0
    state_id = 0
    date_from = ''
    date_until = ''    
    condiciones = Q()

    if request.method == 'POST':       

        date_from = request.POST.get('dateFrom')
        date_until = request.POST.get('dateUntil')
        type_id = int(request.POST.get('type'))
        state_id = int(request.POST.get('state'))

        if date_from != '':
            # date_from += ' 00:00:00'
            condiciones &= Q(creation_date__gte = date_from) ##fecha mayor o igual

        if date_until != '':
            date_until += ' 23:59:59'
            condiciones &= Q(creation_date__lte = date_until) ##fecha mayor o igual

        if type_id != 0:
            condiciones &= Q(type__id = type_id) ##igual a fk

        if state_id != 0:
            condiciones &= Q(state__id = state_id) ##igual a fk    


    proyects_data = funct_data_proyect(condiciones)
    
    return render(request, 'proyect/panel.html', {'proyects_data': proyects_data,
                                                  'date_from': date_from,
                                                  'date_until': date_until,
                                                  'type_id': type_id,
                                                  'state_id': state_id,
                                                  'types': types,
                                                  'states': states})    


@login_required
def proyect_new(request):
     
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
        customer_data = funct_data_customer(condicionesCustomer, 1)

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
                                                            state=State.objects.get(id=state_Id),
                                                            # date=date, 
                                                            description=proyect_description,                                                        
                                                            created_by_user = request.user.id,
                                                            modification_by_user = request.user.id)
                    proyect_id = proyect_save.id

                    

                    for decorator_id in decorators_ids:
                        decorator = Decorator.objects.get(id = decorator_id)
                        decorator.proyects.add(proyect_save)

                        #Iniciales del nombre, si es através de Cliente
                        if type_id == '2':
                            partes = decorator.name.split()
                            code += ''.join([parte[0].upper() for parte in partes])

                    for decorator_id in ascociate_ids:
                        decorator = Decorator.objects.get(id = decorator_id)
                        decorator.proyects.add(proyect_save)


                    #Se actualiza el código, una vez que se obtiene el Id.                
                    code += f"{proyect_id:03d}"
                    proyect_save.code =  code
                    proyect_save.save()

                    # Event.objects.create( type_event_id=1,                                        
                    #                         proyect_id=proyect_id, 
                    #                         user=request.user.id)
                    
                    saveEvent(request, 1, proyect_id, None)
            
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
        decorators = Decorator.objects.filter(is_supervisor=1, status=1).order_by('name')
        type_select = types.first()

        return render(request, 'proyect/new.html', 
                    {'types': types,
                    'type_select': type_select,
                    'decorators': decorators
                    # 'customers': customers,
                    })


@login_required
def proyect_view(request, proyect_id):
    
    proyect = Proyect.objects.get(id = proyect_id) #obtiene solo un resultado
    customer = proyect.customer    
    category = Category.objects.all().order_by('order','name')
    place = Place.objects.all().order_by('name')

    state_new_name = ''
        
    try:
        decorators = Decorator.objects.filter(proyects = proyect, is_supervisor = 1).order_by('name')
        ascociates = Decorator.objects.filter(proyects = proyect, is_supervisor = 2).order_by('name')
        events = Event.objects.filter(proyect_id = proyect_id).order_by('creation_date')
        state_new = State.objects.filter(id = (proyect.state.id + 1)).first()

        if state_new:
            state_new_name = state_new.name

    except Decorator.DoesNotExist:
        decorators = None
        ascociates = None

    except Event.DoesNotExist:
        events = None

    except State.DoesNotExist:
        state_new_name = ''

    itemsHtml = funct_data_items(proyect_id)
    advance = retornarAdvance(proyect.state.id)

    decoratorsHTML = funct_table_decorators(decorators)
    ascociatesHTML = funct_table_decorators(ascociates)
    notesHTML = funct_data_events(proyect_id)



                        
    return render(request, 'proyect/view.html',{'proyect': proyect,
                                                'customer': customer,
                                                'decorators': decorators,
                                                'events':events,
                                                'categories':category,                                                
                                                'places': place,
                                                'itemsHtml': itemsHtml,
                                                'state_new': state_new_name,
                                                'advance':advance,
                                                'decoratorsHTML': decoratorsHTML,
                                                'ascociatesHTML': ascociatesHTML,
                                                'notesHTML': notesHTML,})  


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
    

@login_required
def getDataProyectCustomer(request):
    #Consulta los proyectos desde la base de datos
    proyects_data = funct_data_proyect(None)
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'proyects': proyects_data})


@login_required
def getDataDecorator(request):
    #Consulta los decoradores desde la base de datos
    selected_values_str = request.POST.get('idsSelect')
    selected_values = selected_values_str.split(',')
    selected_values = [int(id_value) for id_value in selected_values]
     
    # print("Valores recibidos: ", selected_values)

    decorators = Decorator.objects.filter(id__in =selected_values)    
        
    decoratorsHTML = funct_table_decorators(decorators)
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


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
            customer_data = funct_data_customer(condicionesCustomer, 1)

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


@login_required
def getDataCalendar(request):
    #Consulta los items desde la BD    
    items = Item.objects.filter(date_end__isnull=False)
    events = []

    for item in items:

        if item.date_end:

            fecha = timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M')
            color = '',

            if item.proyect.state.id == 4:
                color = '#50cd89'

            if item.proyect.state.id == 5:
                color = '#7239ea'

            if item.proyect.state.id == 6:
                color = 'fc-event-solid-dark'

            if item.proyect.state.id == 7:
                color = 'fc-event-solid-dark'
                    
            events.append({
                'id': item.id,
                'title':  item.proyect.customer.address,
                'start': fecha,
                'description': item.proyect.customer.name,
                'color': color,
                'groupId': "/proyect/view/" + str(item.proyect.id),
            })
                
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'calendar': events})


@login_required
def getDataCalendar(request):
    #Consulta los items desde la BD    
    items = Item.objects.filter(date_end__isnull=False)
    events = []

    for item in items:

        if item.date_end:

            fecha = timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M')
            color = '',

            if item.proyect.state.id == 4:
                color = '#50cd89'

            if item.proyect.state.id == 5:
                color = '#7239ea'

            if item.proyect.state.id == 6:
                color = 'fc-event-solid-dark'

            if item.proyect.state.id == 7:
                color = 'fc-event-solid-dark'
                    
            events.append({
                'id': item.id,
                'title':  item.proyect.customer.address,
                'start': fecha,
                'description': item.proyect.customer.name,
                'color': color,
                'groupId': str(item.proyect.id),
            })
                
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'calendar': events})
    
    
@login_required
def getDataComment(request):
    #Consulta los decoradores desde la base de datos    
    proyectId = request.GET.get('id1')
    itemId = request.GET.get('id2')
    itemHtml = funct_data_item_comment(proyectId, itemId)
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': itemHtml})


###############################
### Elementos dependientes  ###
###############################

@login_required
def selectAscociate(request):
    #Consulta los decoradores desde la base de datos
    selected_values_str = request.POST.get('decoratorsSelect')
    selected_values = selected_values_str.split(',')
    selected_values = [int(id_value) for id_value in selected_values]     

    supervisors = Decorator.objects.filter(id__in =selected_values,is_supervisor=1)
    decorators = Decorator.objects.filter(supervisor__in = supervisors).order_by('name')

    decoratorsHTML = ''

    for decorator in decorators:  
        # print("Valores recibidos: ", decorator.id )
        decoratorsHTML += '<option value=' + str(decorator.id) + '>' + decorator.name + '</option>'
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


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


@login_required
def selectGroup(request):
    #Consulta las subcategorias desde la base de datos
    category_value = request.POST.get('categorySelect')
    subcategory_value = request.POST.get('subcategorySelect')
    groupHTML = ''

    if subcategory_value == '':
        subcategory_value = 0

    try:
        groups = Group.objects.filter(category = Category.objects.get(id = category_value), subcategory = Subcategory.objects.get(id = subcategory_value)).order_by('order','name')
       
        for group in groups:          
            groupHTML += '<option value=' + str(group.id) + '>' + group.name + '</option>'

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': groupHTML})


@login_required
def selectAttibutes(request):
    #Consulta las subcategorias desde la base de datos
    selected_value = request.POST.get('categorySelect')    
    attributeHTML = ''

    try:

        attributes = Category_Attribute.objects.filter(category = Category.objects.get(id = selected_value)).order_by('order','attribute')
        
        for atribute in attributes:          
            attributeHTML += '<div class="row mb-2">'
            attributeHTML += '<div class="col-xl-3"><div class="fs-7 fw-bold mt-2 mb-3">' + atribute.attribute.name + ':</div></div>'
            attributeHTML += '<div class="col-xl-8"><input name="attribute_' + str(atribute.attribute.id) + '" type="text" class="form-control form-control-solid" maxlength="150" placeholder="' + atribute.attribute.description + '"/></div></div>'

    except ValueError:
        messages.error(request, 'Server error. Please contact to administrator!')
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': attributeHTML})


@login_required
def selectItems(request):
    #Consulta los items desde la base de datos
    selected_value = request.POST.get('proyect_id')        
    itemsHTML = funct_data_items(selected_value)    
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': itemsHTML})

  

###################################
## Funciones para obtener datos ###
###################################

def funct_data_proyect(filters):

    proyects_data = []

    if filters:
        proyects = Proyect.objects.filter(filters).order_by('-id')        
    else:
        proyects = Proyect.objects.all().order_by('-id')


    # Creamos una lista con los datos de cada proyecto
    
    fecha_actual = datetime.now()

    for proyect in proyects:

        # parsed_date = ''
        allDay = False

        # try:
        #     if len(proyect.date) == 17:
        #         parsed_date = proyect.date
        #         parsed_date = str(datetime.strptime(parsed_date, "%Y-%m-%d, %H:%M"))
            
        #     elif len(proyect.date) == 10:            
        #         allDay = True
        #         parsed_date = str(datetime.strptime(proyect.date + ', 00:00', "%Y-%m-%d, %H:%M"))
        #     else:
        #         parsed_date = '1900-01-01, 00:00'    
                
        # except ValueError:
        #     parsed_date = '1900-01-01, 00:00'
        
        #######################################
        
        decorators = Decorator.objects.filter(proyects = proyect, is_supervisor = 1).order_by('name')
        decoratorsStr = ''

        for decorator in decorators:              
            decoratorsStr += decorator.name + ' '

        #######################################

        items = Item.objects.filter(proyect = proyect).order_by('category')
        categoryList = []
        categoryStr = ''
        
        for item in items:
            if item.category.name not in categoryList:
                categoryList.append(item.category.name)
        
        for category in categoryList:            
            categoryStr += category + ','

        categoryStr = categoryStr[:-1]
        #######################################

        qty_wo = Item.objects.filter(proyect = proyect).count()

        fecha_creacion = proyect.creation_date
        fecha_creacion = fecha_creacion.replace(tzinfo=None)
        fecha_actual = fecha_actual.replace(tzinfo=None)
        difference = fecha_actual - fecha_creacion

        proyects_data.append({
            'id': proyect.id,
            'customerName': proyect.customer.name,
            'address': proyect.customer.address,
            'city': proyect.customer.city,
            'state_u': proyect.customer.state,
            'zipcode': proyect.customer.zipcode,
            'apartment': proyect.customer.apartment,            
            'creationDate': fecha_creacion.strftime("%Y-%m-%d"),
            'email': proyect.customer.email,
            'state_id': proyect.state.id,
            'state': proyect.state.name,
            'allDay': allDay,
            'difference': difference.days,
            'decorators': decoratorsStr,
            'qty_wo': qty_wo,
            'categories': categoryStr,
        })
    
    return proyects_data
    

def funct_data_customer(filtersCustomer, caso):

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


def funct_data_event(filters):
    
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


def funct_data_items(proyect_id):
    
    itemsHTML = ""

    try:

        proyect = Proyect.objects.get(id=proyect_id)

        items = Item.objects.filter(proyect = proyect).order_by('id')
        itemN = 0
        
        for item in items:

            fecha_propuesta = ''
            code = ''
            group = ''
            itemN+= 1

            try:
                if item.date_proposed:

                    fecha_propuesta = timezone.localtime(item.date_proposed).strftime('%Y-%m-%d')

                # if item.date_end:
                #     fecha_fin = timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M')

                if proyect.code:
                    code = proyect.code + '-' + str(itemN)

                else:
                    code = str(itemN)
            
            except ValueError:
                messages.error('Server error. Date not exist!')
            

            itemsHTML += '<div class="row itemCount" style="border: 1px solid #d7d9dc; border-radius: .475rem">'

            itemsHTML += '<div class="col-lg-12">'
            itemsHTML += '<div class="col-lg-8">'
            itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3"><b>' + code  + '</b>'
            itemsHTML += '<div class="h-3px w-100 bg-primary col-lg-4">'
            itemsHTML += '</div>'
            itemsHTML += '</div>'
            itemsHTML += '</div>'
            itemsHTML += '</div>'
            

            if item.group:
                group = item.group.name

            
            itemsHTML += '<div class="col-lg-8" style="border:1px solid white; border-width:1px;">'
            itemsHTML += '<div class="row mb-6">'
            # itemsHTML += '<div class="col-lg-12" style="border:1px solid yellow; border-width:1px;">'

            ## Celda 1 (cabecera) ##                        
            itemsHTML += '<div class="col-xl-6" style="border:1px solid white; border-width:1px;">'
            itemsHTML += '<table><tbody>'                
            itemsHTML += '<tr><td><b>Category:</b> ' + item.category.name + '</td></tr>'
            itemsHTML += '<tr><td><b>Sub Category:</b> ' + item.subcategory.name + '</td></tr>'
            itemsHTML += '<tr><td><b>Group:</b> ' + group + '</td></tr>'
            itemsHTML += '<tr><td><b>Place:</b> ' + item.place.name + '</td></tr>'
            itemsHTML += '<tr><td><b>QTY:</b> ' + item.qty + '</td></tr>'
            itemsHTML += '<tr><td><b>Proposed date:</b> ' + fecha_propuesta + '</td></tr>'
            itemsHTML += '<tr><td><b>Notes:</b> ' + item.notes + '</td></tr>'        
            itemsHTML += '</tbody></table>'
            itemsHTML += '</div>'          
            #############

            ## Celda 2 (atributos) ##                        
            itemsHTML += '<div class="col-xl-6" style="border:1px solid white; border-width:1px;">'
            itemsHTML += '<table><tbody>'         

            attributes = Item_Attribute.objects.filter(item = Item.objects.get(id=item.id))
            for attribute in attributes:
                itemsHTML += '<tr><td><b>' + attribute.attribute.name + ':</b> ' + attribute.notes + '</td></tr>'

            itemsHTML += '</tbody></table>'
            itemsHTML += '</div>'       
            #############

            ## Celda 3 (archivos) ##
            itemsHTML += '<div class="col-lg-12" style="border:1px solid white; border-width:1px;">'            
            itemsHTML += '<div class="row">'        
            itemsHTML += '<div class="col-xl-12">'                        

            files = Item_Files.objects.filter(item = Item.objects.get(id=item.id))

            if len(files) > 0:                
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
                                                    
                    itemsHTML += '<span>'
                    itemsHTML += '<a href="' + file.file.url + '" class="fs-7 text-hover-primary">' + file.name + '</a>'
                    itemsHTML += '<div class="text-gray-400">' + file.notes + '</div>'
                    itemsHTML += '</<span>' 

                    itemsHTML += '</li>'

                itemsHTML += '</ul>'
                itemsHTML += '</div>'

            itemsHTML += '</div>'
            itemsHTML += '</div>'
            itemsHTML += '</div>'
            #############


            ## Celda 5 (imagenes) ##
            itemsHTML += '<div class="col-lg-12" style="border:1px solid white; border-width:1px;">'
            itemsHTML += '<div class="row">'        
            itemsHTML += '<div class="col-xl-12">'
            
            itemsHTML += '<section class="grid-gallery-section">'
            
            # itemsHTML += '<div id="gallery-filters" class="gallery-button-group">'
            # itemsHTML += '<button class="filter-button is-checked showImg" data-filter="*">ALL FILES</button>'
            # itemsHTML += '<button class="filter-button" data-filter=".Image">IMAGES</button>'
            # itemsHTML += '<button class="filter-button" data-filter=".Material">MATERIAL</button>'
            # itemsHTML += '</div>'
            
            itemsHTML += '<div class="grid-gallery">'
            itemsHTML += '<div class="gallery-grid-sizer"></div>'            		

            images = Item_Images.objects.filter(item = Item.objects.get(id=item.id))
            for image in images:

                type_imp = ''
                
                if image.type == 1:
                    type_imp = 'Image'

                elif image.type == 2:
                    type_imp = 'Material'

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

                # itemsHTML += '<tr><td><div class="image-container"><img src="" alt="' + image.name + '" class="preview"></div></td><td>' + image.notes + '</td></tr>'

            itemsHTML += '</div>'
            itemsHTML += '</section>'


            itemsHTML += '</div>'
            itemsHTML += '</div>'
            itemsHTML += '</div>'
            
            #############


            itemsHTML += '</div>' # Final row
            itemsHTML += '</div>' # Final col



            ## Celda 5 (acciones) ##
            itemsHTML += '<div class="col-lg-4" style="border:1px solid white; border-width:1px;">'
            itemsHTML += '<div class="row">'
            itemsHTML += '<div class="col-xl-12">'

            if proyect.state.id == 1:
                                                        
                itemsHTML += '<div class="d-flex justify-content-center flex-shrink-0">'
                itemsHTML += '<a href="#" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm me-1"><span class="svg-icon svg-icon-3" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M21.4 8.35303L19.241 10.511L13.485 4.755L15.643 2.59595C16.0248 2.21423 16.5426 1.99988 17.0825 1.99988C17.6224 1.99988 18.1402 2.21423 18.522 2.59595L21.4 5.474C21.7817 5.85581 21.9962 6.37355 21.9962 6.91345C21.9962 7.45335 21.7817 7.97122 21.4 8.35303ZM3.68699 21.932L9.88699 19.865L4.13099 14.109L2.06399 20.309C1.98815 20.5354 1.97703 20.7787 2.03189 21.0111C2.08674 21.2436 2.2054 21.4561 2.37449 21.6248C2.54359 21.7934 2.75641 21.9115 2.989 21.9658C3.22158 22.0201 3.4647 22.0084 3.69099 21.932H3.68699Z" fill="black" /><path d="M5.574 21.3L3.692 21.928C3.46591 22.0032 3.22334 22.0141 2.99144 21.9594C2.75954 21.9046 2.54744 21.7864 2.3789 21.6179C2.21036 21.4495 2.09202 21.2375 2.03711 21.0056C1.9822 20.7737 1.99289 20.5312 2.06799 20.3051L2.696 18.422L5.574 21.3ZM4.13499 14.105L9.891 19.861L19.245 10.507L13.489 4.75098L4.13499 14.105Z" fill="black" /></svg></span></a>'
                itemsHTML += '<a href="javascript:del(' + str(item.id) + ')" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm"><span class="svg-icon svg-icon-3" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 9C5 8.44772 5.44772 8 6 8H18C18.5523 8 19 8.44772 19 9V18C19 19.6569 17.6569 21 16 21H8C6.34315 21 5 19.6569 5 18V9Z" fill="black" /><path opacity="0.5" d="M5 5C5 4.44772 5.44772 4 6 4H18C18.5523 4 19 4.44772 19 5V5C19 5.55228 18.5523 6 18 6H6C5.44772 6 5 5.55228 5 5V5Z" fill="black" /><path opacity="0.5" d="M9 4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V4H9V4Z" fill="black" /></svg></span></a>'
                itemsHTML += '</div>'


            if proyect.state.id >= 2:
 
                if proyect.state.id == 3:
                    
                    itemsHTML += comments_state(item, 2)
                    
                if proyect.state.id == 4:
                    
                    itemsHTML += comments_state(item, 2)
                    itemsHTML += comments_state(item, 3)

                if proyect.state.id == 5:
                    
                    itemsHTML += comments_state(item, 2)
                    itemsHTML += comments_state(item, 3)
                    itemsHTML += comments_state(item, 4)

                if proyect.state.id == 6:
                    
                    itemsHTML += comments_state(item, 2)
                    itemsHTML += comments_state(item, 3)
                    itemsHTML += comments_state(item, 4)
                    itemsHTML += comments_state(item, 5)

                if proyect.state.id == 7:
                    
                    itemsHTML += comments_state(item, 2)
                    itemsHTML += comments_state(item, 3)
                    itemsHTML += comments_state(item, 4)
                    itemsHTML += comments_state(item, 5)
                    itemsHTML += comments_state(item, 6)

                ##################################################################################

                if proyect.state.id != 7:
                    
                    itemsHTML += funct_data_item_comment(proyect_id, item.id)
                  
            
            itemsHTML += '</div>'
            itemsHTML += '</div>'                        
            itemsHTML += '</div>'
            #############

            itemsHTML += '</div><br/>' # Final

    except ValueError:
        messages.error('Server error. Please contact to administrator!')
        
    return itemsHTML


def funct_data_events(proyect_id):
    
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


def funct_data_item_comment(proyect_id, item_Id):
    
    proyect = Proyect.objects.get(id=proyect_id)
    items = Item.objects.filter(proyect = proyect, id = item_Id).order_by('id')
        
    itemsHTML = ''    
    itemTxt = ''
    fecha_fin = ''
    
            
    for item in items:

        itemCS = Item_Comment_State.objects.filter(item=item, state=proyect.state).first()
        itemCSF = Item_Comment_State_Files.objects.filter(item_comment_state = itemCS)

        if itemCS:
            itemTxt = itemCS.notes

        if item.date_end:
            fecha_fin = timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M')

        itemsHTML += '<div class="d-flex justify-content-start flex-shrink-0">'
        itemsHTML += '<div class="col-xl-12 fv-row text-start">'
        itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3">Notes:</div>'
        itemsHTML += '<form id="formItem_' + str(item.id) + '" method="POST" enctype="multipart/form-data">'
        itemsHTML += '<textarea name="notes" class="form-control form-control-solid h-80px" maxlength="2000">' + itemTxt + '</textarea><br/>'
                        
        if proyect.state.id == 4 or proyect.state.id == 5:

            responsibles = Responsible.objects.filter(status = 1).order_by('name')

            itemsHTML += '<div class="col-xl-12 fv-row">'
            itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3">Responsible:</div>'
            itemsHTML += '<select class="form-select form-select-sm form-select-solid" data-kt-select2="true" data-placeholder="Select..." data-allow-clear="True" name="responsable" >'
            itemsHTML += '<option value="0">---</option>'

            for responsible in responsibles:
                if item.responsible.id == responsible.id:
                    itemsHTML += '<option value=' + str(responsible.id) + ' selected>' + responsible.name + '</option>'
                else:

                    itemsHTML += '<option value=' + str(responsible.id) + '>' + responsible.name + '</option>'

            itemsHTML += '</select>'
            itemsHTML += '</div>'

            
            itemsHTML += '<div class="col-xl-6 fv-row">'
            itemsHTML += '<div class="fs-7 fw-bold mt-2 mb-3">End date:</div>'
            itemsHTML += '<span class="svg-icon position-absolute ms-4 mb-1 svg-icon-2">'
            itemsHTML += '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
            itemsHTML += '<path opacity="0.3" d="M21 22H3C2.4 22 2 21.6 2 21V5C2 4.4 2.4 4 3 4H21C21.6 4 22 4.4 22 5V21C22 21.6 21.6 22 21 22Z" fill="black" />'
            itemsHTML += '<path d="M6 6C5.4 6 5 5.6 5 5V3C5 2.4 5.4 2 6 2C6.6 2 7 2.4 7 3V5C7 5.6 6.6 6 6 6ZM11 5V3C11 2.4 10.6 2 10 2C9.4 2 9 2.4 9 3V5C9 5.6 9.4 6 10 6C10.6 6 11 5.6 11 5ZM15 5V3C15 2.4 14.6 2 14 2C13.4 2 13 2.4 13 3V5C13 5.6 13.4 6 14 6C14.6 6 15 5.6 15 5ZM19 5V3C19 2.4 18.6 2 18 2C17.4 2 17 2.4 17 3V5C17 5.6 17.4 6 18 6C18.6 6 19 5.6 19 5Z" fill="black" />'
            itemsHTML += '<path d="M8.8 13.1C9.2 13.1 9.5 13 9.7 12.8C9.9 12.6 10.1 12.3 10.1 11.9C10.1 11.6 10 11.3 9.8 11.1C9.6 10.9 9.3 10.8 9 10.8C8.8 10.8 8.59999 10.8 8.39999 10.9C8.19999 11 8.1 11.1 8 11.2C7.9 11.3 7.8 11.4 7.7 11.6C7.6 11.8 7.5 11.9 7.5 12.1C7.5 12.2 7.4 12.2 7.3 12.3C7.2 12.4 7.09999 12.4 6.89999 12.4C6.69999 12.4 6.6 12.3 6.5 12.2C6.4 12.1 6.3 11.9 6.3 11.7C6.3 11.5 6.4 11.3 6.5 11.1C6.6 10.9 6.8 10.7 7 10.5C7.2 10.3 7.49999 10.1 7.89999 10C8.29999 9.90003 8.60001 9.80003 9.10001 9.80003C9.50001 9.80003 9.80001 9.90003 10.1 10C10.4 10.1 10.7 10.3 10.9 10.4C11.1 10.5 11.3 10.8 11.4 11.1C11.5 11.4 11.6 11.6 11.6 11.9C11.6 12.3 11.5 12.6 11.3 12.9C11.1 13.2 10.9 13.5 10.6 13.7C10.9 13.9 11.2 14.1 11.4 14.3C11.6 14.5 11.8 14.7 11.9 15C12 15.3 12.1 15.5 12.1 15.8C12.1 16.2 12 16.5 11.9 16.8C11.8 17.1 11.5 17.4 11.3 17.7C11.1 18 10.7 18.2 10.3 18.3C9.9 18.4 9.5 18.5 9 18.5C8.5 18.5 8.1 18.4 7.7 18.2C7.3 18 7 17.8 6.8 17.6C6.6 17.4 6.4 17.1 6.3 16.8C6.2 16.5 6.10001 16.3 6.10001 16.1C6.10001 15.9 6.2 15.7 6.3 15.6C6.4 15.5 6.6 15.4 6.8 15.4C6.9 15.4 7.00001 15.4 7.10001 15.5C7.20001 15.6 7.3 15.6 7.3 15.7C7.5 16.2 7.7 16.6 8 16.9C8.3 17.2 8.6 17.3 9 17.3C9.2 17.3 9.5 17.2 9.7 17.1C9.9 17 10.1 16.8 10.3 16.6C10.5 16.4 10.5 16.1 10.5 15.8C10.5 15.3 10.4 15 10.1 14.7C9.80001 14.4 9.50001 14.3 9.10001 14.3C9.00001 14.3 8.9 14.3 8.7 14.3C8.5 14.3 8.39999 14.3 8.39999 14.3C8.19999 14.3 7.99999 14.2 7.89999 14.1C7.79999 14 7.7 13.8 7.7 13.7C7.7 13.5 7.79999 13.4 7.89999 13.2C7.99999 13 8.2 13 8.5 13H8.8V13.1ZM15.3 17.5V12.2C14.3 13 13.6 13.3 13.3 13.3C13.1 13.3 13 13.2 12.9 13.1C12.8 13 12.7 12.8 12.7 12.6C12.7 12.4 12.8 12.3 12.9 12.2C13 12.1 13.2 12 13.6 11.8C14.1 11.6 14.5 11.3 14.7 11.1C14.9 10.9 15.2 10.6 15.5 10.3C15.8 10 15.9 9.80003 15.9 9.70003C15.9 9.60003 16.1 9.60004 16.3 9.60004C16.5 9.60004 16.7 9.70003 16.8 9.80003C16.9 9.90003 17 10.2 17 10.5V17.2C17 18 16.7 18.4 16.2 18.4C16 18.4 15.8 18.3 15.6 18.2C15.4 18.1 15.3 17.8 15.3 17.5Z" fill="black" />'
            itemsHTML += '</svg>'
            itemsHTML += '</span>'
            itemsHTML += '<input class="form-control form-control-solid ps-12 date-picker" name="date_end" placeholder="Pick a date" value="' + fecha_fin + '"/>'
            itemsHTML += '</div><br/>'
            
        if itemCSF:
            
            itemsHTML += '<ul class="text-start">'
            
            for file in itemCSF:
                itemsHTML += '<li><a href=' + file.file.url + '>' + file.name + '</a>  <a href="" onClick="delImC(this, ' + str(file.id) + ', ' + str(itemCS.id) + ', ' + str(item.id) + ')"<i class="fa fa-trash"></i></a>'
                
            itemsHTML += "</ul>"
        
        itemsHTML += '<input type="file" name="files" class="form-control form-control" multiple><br/>'
        itemsHTML += '<div class="row">'
        itemsHTML += '<div class="col-md-3">'

        itemsHTML += '<button type="button" class="btn btn-primary px-8 py-2 mr-2" onclick="saveIC(' + str(item.id) + ')">Save</button>'                
        itemsHTML += '</div>'
        itemsHTML += '<div class="col-md-9">'                                    
        itemsHTML += '<div class="divItemMsg alert alert-success text-start p-2 mb-1" style="display:none">The data has been saved successfully.</div>'
        
        itemsHTML += '</div>'                                
        itemsHTML += '</div>'
                            
        itemsHTML += '</form><br/><br/>'
        itemsHTML += '</div>'
        itemsHTML += '</div>'

    return itemsHTML


###################################
## Funciones para guardar datos ###
###################################

@login_required
def saveEvent(request, type_event_id, proyect_id, description):

    # EVENTOS = [
    #         (0, 'Other'),
    #         (1, 'Create proyect'),
    #         (2, 'Comment'),
    #         (3, 'Create item'),
    #         (4, 'Delete item'),
    #         (5, 'Upload file/comment'),        
    #         (6, 'Change state'),
    #     ]
    try:

        proyect = Proyect.objects.get(id = proyect_id)

        Event.objects.create(   type_event_id=type_event_id,                                        
                                proyect=proyect, 
                                description = description,
                                user=request.user.id)
        
    except Proyect.DoesNotExist:        
        messages.error('Server error. Please contact to administrator!')
    

@login_required
def saveItem(request):

    item_id = 0

    if request.method == 'POST':
        proyect_id = request.POST.get('proyect_id')        
        category_id = request.POST.get('category') 
        subcategory_id = request.POST.get('subcategory')
        group_id = request.POST.get('group')
        place_id = request.POST.get('place')
        qty = request.POST.get('qty')
        notes = request.POST.get('notes')
        date_proposed = request.POST.get('date_proposed')
            
        try:
            
            item_save = Item.objects.create(proyect = Proyect.objects.get(id=proyect_id),
                                            category = Category.objects.get(id=category_id),
                                            subcategory = Subcategory.objects.get(id=subcategory_id),
                                            group = Group.objects.get(id=group_id),
                                            place = Place.objects.get(id=place_id),
                                            qty = qty,
                                            notes = notes,
                                            date_proposed = date_proposed,
                                            created_by_user = request.user.id,
                                            modification_by_user = request.user.id)
            item_id = item_save.id

            saveEvent(request, 3, proyect_id, None)


            ################################### Se recorren los atributos ###################################
            
            data = request.POST

            prefijo = "attribute_"

            for key, value in data.items():
                if key.startswith(prefijo) and value.strip() != "":
                    try:

                        attribute_id = int(key[len(prefijo):])

                        Item_Attribute.objects.create(  item = Item.objects.get(id=item_id),
                                                        attribute = Attribute.objects.get(id=attribute_id),
                                                        notes = value)

                    except ValueError:
                        messages.error(request, 'Server error. Please contact to administrator!')


            ################################### Se recorren las imagenes ###################################

            files = request.FILES

            prefijo = 'inputImg_'            

            for key, value in files.items():
                
                if key.startswith(prefijo) and validateTypeFile(value.content_type):
                    try:

                        file = request.FILES.get(key)
                        notes = ''
                        try:

                            id = int(key[len(prefijo):])
                            notes = data.get('txtImgNotes_' + str(id))

                            type_num = 1
                            type_str = data.get('chkImgType_' + str(id))

                            if type_str == 'on':
                                type_num = 2


                            try:
                                # Abrir la imagen usando PIL
                                imagen = Image.open(file)

                                if imagen:

                                    Item_Images.objects.create( item = Item.objects.get(id=item_id),
                                                                file = file,
                                                                name = value.name,
                                                                type = type_num,
                                                                notes = notes)


                            except OSError: #Guardarlo como archivo adjunto

                                Item_Files.objects.create( item = Item.objects.get(id=item_id),
                                                            file = file,
                                                            name = value.name,
                                                            type = type_num,
                                                            notes = notes)


                            except:
                                messages.error(request, 'Text images not found!')        


                        except:                            
                            messages.error(request, 'Text images not found!')
                                                    
                    except ValueError:
                        messages.error(request, 'Server error. Please contact to administrator!')


        except ValueError:
            messages.error(request, 'Server error. Please contact to administrator!')


    return JsonResponse({'result': item_id})


@login_required
def saveItemComment(request):
    
    if request.method == 'POST':
        proyect_id = request.POST.get('id1')
        item_id = request.POST.get('id2')
        notes = request.POST.get('notes')
        date_end = request.POST.get('date_end')
        responsible_id = request.POST.get('responsable')

        proyect = Proyect.objects.get(id=proyect_id)
        item = Item.objects.get(proyect = proyect, id=item_id)
        
        if item:

            item_coment = Item_Comment_State.objects.filter(item=item, state=proyect.state).first()

            if date_end:
                item.date_end = date_end
                item.save()

            if responsible_id:

                if int(responsible_id):

                    if Responsible.objects.get(id=responsible_id):                                    
                        item.responsible = Responsible.objects.get(id=responsible_id)
                        item.save()
                            
            if item_coment == None:

                item_coment_save = Item_Comment_State.objects.create(   item = item,
                                                                        state = proyect.state,
                                                                        notes = notes,
                                                                        created_by_user = request.user.id,
                                                                        modification_by_user = request.user.id)
            else:

                item_coment_save = item_coment
                item_coment_save.notes = notes
                item_coment_save.modification_by_user = request.user.id
                item_coment_save.save()

            ################################### Se recorren los archivos ###################################

            files = request.FILES.getlist('files[]')

            for file in files:
                
                if validateTypeFile(file.content_type):
                    try:
                        
                        Item_Comment_State_Files.objects.create(    item_comment_state = item_coment_save,
                                                                        file = file,
                                                                        name = file.name)
                    except:                        
                        messages.error(request, 'Server error. Please contact to administrator!')

            return JsonResponse({'result': "OK"})


##################################
## Funciones para borrar datos ###
##################################

@login_required
def deleteItem(request):
    item_id = request.POST.get('i') 
    status = 0

    try:
        item = Item.objects.get(id = item_id)
        item.delete()
        status = 1

        saveEvent(request, 4, item.proyect.id, None) ## Borrar item

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


@login_required
def deleteProyect(request):
    proyect_id = request.POST.get('i') 
    status = 0

    try:
        proyect = Proyect.objects.get(id = proyect_id)
        proyect.delete()
        status = 1

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


@login_required
def deleteItemCommentFile(request):
    id = request.POST.get('i') 
    item_cst_id = request.POST.get('t')
    item_id = request.POST.get('e')
    proyect_id = request.POST.get('p')
    status = 0

    try:
        itemCS = Item_Comment_State.objects.get(id = item_cst_id)
        itemCSF = Item_Comment_State_Files.objects.get(id = id, item_comment_state = itemCS)

        if itemCSF.item_comment_state.item.proyect.id == int(proyect_id) and itemCSF.item_comment_state.item.id == int(item_id): #Si pertenece al proyecto, se borra
            itemCSF.delete()        
            status = 1
        else:
            status = 2

        # saveEvent(request, 4, item.proyect.id, None) ## Borrar item

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})

##################################
## Funciones para actualizar datos ###
##################################

@login_required
def updateStatus(request):
    proyect_id = request.POST.get('i') 
    status = 0

    try:
        proyect = Proyect.objects.get(id = proyect_id)
        proyect.state = State.objects.get(id = (proyect.state.id + 1))
        proyect.save()

        description = "Change to status:" + proyect.state.name

        Event.objects.create(   type_event_id = 6,                                        
                                proyect=proyect, 
                                description = description,
                                user=request.user.id)

        
        status = 1

    except ValueError:
        status = -1
        messages.error('Server error. Please contact to administrator!')

    return JsonResponse({'result': status})


##################################
## Funciones para validar ###
##################################


def validateTypeFile(value):

    isfileValidate = False

    try:                
        # Tipos permitidos
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg', 'image/bmp','image/mpo','application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']

        if value in tipos_permitidos:            
            isfileValidate = True

    except IOError:
        # raise ValidationError(f'El archivo debe ser una imagen de tipo: {", ".join(tipos_permitidos)}')
        raise ValidationError("El archivo no es una imagen válida.")
    
    return isfileValidate


##################################
## Funciones varias ###
##################################


def retornarAdvance(value):

    adv = 0
    factor = 15 #14.28
    adv = value * factor
    
    return adv


def funct_table_decorators(decorators):
    
    # Creamos una lista con los datos de cada proyecto

    decoratorsHTML = ''

    if len(decorators) > 0:

        decoratorsHTML = '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-7 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
        decoratorsHTML += '<th title="Field #1">Name</th>'
        decoratorsHTML += '<th title="Field #2">Email</th>'
        decoratorsHTML += '<th title="Field #3">Phone</th>'
        decoratorsHTML += '<th title="Field #4">Address</th>'
        decoratorsHTML += '<th title="Field #5">Apt-ste-floor</th>'
        decoratorsHTML += '<th title="Field #6">City</th>'
        decoratorsHTML += '<th title="Field #7">State</th>'
        decoratorsHTML += '<th title="Field #8">Zipcode</th>'
        
        decoratorsHTML += '</tr></thead><tbody>'

        for decorator in decorators:  
            decoratorsHTML += '<tr>'
            decoratorsHTML += '<td class="text-start fs-7">' + decorator.name + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.email + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.phone + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.address + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.apartment + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.city + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.state + '</td>'
            decoratorsHTML += '<td class="text-start text-muted fs-7">' + decorator.zipcode + '</td>'        
            decoratorsHTML += '</tr>'
        
        decoratorsHTML += '</tbody></table>'

    return decoratorsHTML


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


def comments_state(item, state_id):

    itemsHTML = ''

    itemTxt = ''
    itemCS = Item_Comment_State.objects.filter(item=item, state=State.objects.get(id = state_id)).first()
    itemCSF = Item_Comment_State_Files.objects.filter(item_comment_state = itemCS)
    
    if itemCS:
        
        itemTxt = itemCS.notes
        
        itemsHTML += '<div class="w-100 d-flex flex-column rounded-3 bg-light bg-opacity-75 py-5 px-5">'
        itemsHTML += '<b>' + State.objects.get(id = state_id).name + ':</b>' + itemTxt
        
        if itemCSF:
            itemsHTML += '<ul class="text-start">'
            for file in itemCSF:
                            #  itemsHTML += "<li><a href=" + file.file.url + " target='_blank'>" + file.name + "</a></li>"
                itemsHTML += '<li><a href=' + file.file.url + '>' + file.name + '</a>'
            itemsHTML += "</ul>"
        
        itemsHTML += '</div><br/>'

    return itemsHTML


def generate_pdf(request, proyect_id):
    try:
        project = Proyect.objects.get(id=proyect_id)
    except Proyect.DoesNotExist:
        raise Http404("El proyecto no existe")
    
    htmlCabecera = ""
    
    if project:

        #Cabecera cliente

        htmlCabecera += "<table class='table_wo'>"
        
        address = ''

        if project.customer.address != "":
            address += project.customer.address

        if project.customer.apartment != "":
            address += "," + project.customer.apartment

        if project.customer.city != "":
            address += "," + project.customer.city

        if project.customer.state != "":
            address += "," + project.customer.state

        if project.customer.zipcode != "":
            address += "," + project.customer.zipcode
        
        name = project.customer.name if str(project.customer.name) != "" else "--"
        phone = project.customer.phone if str(project.customer.phone) != "" else "--"
        email = project.customer.email if str(project.customer.email) != "" else "--"

        htmlCabecera += "<tr><th>Address:</th><td>" + address + "</td></tr>"
        htmlCabecera += "<tr><th>Customer:</th><td>" + str(name) + "</td></tr>"      
        htmlCabecera += "<tr><th>Phone:</th><td>" + str(phone) + "</td></tr>"
        htmlCabecera += "<tr><th>Email:</th><td>" + str(email) + "</td></tr>"
        htmlCabecera += "</table>"
        
                
        #Cabecera proyecto
        htmlCabecera += "<table class='table_wo'>"

        code = project.code if str(project.code) != "" else "--"
        htmlCabecera += "<tr><th>Code:</th><td>" + str(code) + "</td></tr>"

        decorators = Decorator.objects.filter(proyects = project)

        if decorators:

            htmlCabecera += "<tr><th rowspan='" + str(len(decorators)) + "'>Decorator:</th>"
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

        items = Item.objects.filter(proyect = project).order_by("id")                        
                
        if items:
            
            n = 1
            
            for item in items:

                htmlCabecera += "<table class='table_item'>"
                htmlCabecera += "<tr><th colspan='2'>Item: " + str(code) + "-" + str(n) + "</th></tr>"
                n+=1

                category = item.category.name if str(item.category.name) != "" else "--"
                
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
                if item.date_end:             
                    date_end = timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M') if str(timezone.localtime(item.date_end).strftime('%Y-%m-%d %H:%M')) != "" else "--"
                
                notes = item.notes if str(item.notes) != "" else "--"


                htmlCabecera1 = "<table class='table_item_detalle'>"
                htmlCabecera1 += "<tr><td class='td_item'>Category:</td><td>" + str(category) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>Sub Category:</td><td>" + str(subcategory) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>Group:</td><td>" + str(group) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>Place:</td><td>" + str(place) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>QTY:</td><td>" + str(qty) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>Date:</td><td>" + str(date_end) + "</td></tr>"
                htmlCabecera1 += "<tr><td class='td_item'>Notes:</td><td>" + str(notes) + "</td></tr>"
                htmlCabecera1 += "</table>"

                attributes = Item_Attribute.objects.filter(item = item)
                htmlCabecera2 = ""

                if attributes:
                    htmlCabecera2 = "<table class='table_item_detalle'>"
                    
                    for attribute in attributes:

                        name = attribute.attribute.name if str(attribute.attribute.name) != "" else "--"
                        notes = attribute.notes if str(attribute.notes) != "" else "--"
                        htmlCabecera2 += "<tr><td class='td_item'>" + str(name) + ":</td><td>" + str(notes) + "</td></tr>"

                    htmlCabecera2 += "</table>"


                htmlCabecera += "<tr><td style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera1 + "</td><td style='padding:0 0; text-align: left; vertical-align: top;'>" + htmlCabecera2 + "</td></tr>"

                htmlCabecera += "</table>"

                images= Item_Images.objects.filter(item = item)

                if images:
                    
                    htmlCabecera += "<table class='table_item'>"
                    htmlCabecera += "<tr><td colspan='3'><b>Images:</b></td></tr>"
                    htmlCabeceraImg = ""
                    table_img = ""
                    nt = 1
                    for image in images:
                        file = image.file.name if str(image.file.name) != "" else "--"
                        notes = image.notes if str(image.notes) != "" else "--"
                        table_img = "<table><tr><td style='padding:0 0; text-align: center; vertical-align: top; height=180px'><img src='../" + settings.MEDIA_URL + file + "'width='90%'/></td></tr><tr><td style='text-align: left; vertical-align: top;'>" + notes + "</td></tr></table>"                                                
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



    template = get_template('proyect/pdf_template.html')
    context = {
        'CABECERA': htmlCabecera,
        'STATIC_URL': settings.STATIC_URL,
        # 'MEDIA_URL': settings.MEDIA_URL
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="project_{}.pdf"'.format(proyect_id)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generando el PDF', status=500)
    
    return response
