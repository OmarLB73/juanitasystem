from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib import messages
from datetime import datetime # dar formato a la fecha
from django.shortcuts import redirect # redireccionar a páginas
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q # permite realizar consultas complejas
from django.urls import reverse #evita doble envio de formulario


from .models import Type, Responsible, Customer, State, Proyect, Decorator, Event, Category, Subcategory, Place, Catalog #Aquí importamos a los modelos que necesitamos

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

        user_id = request.user.id
        
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
        responsible_id = request.POST.get('responsible')        
        proyect_description = request.POST.get('proyectDescription')
        
        state_Id = 1 #Inicio


            #    if Customer.objects.filter(id=customer_id).exists():
            #         customer_save = Customer.objects.get(id=customer_id)
            #         customer_save.name = customer_name
            #         customer_save.email = email
            #         customer_save.phone = phone
            #         customer_save.description = customer_Description
            #         customer_save.save()


        #Se guarda los datos del cliente
        customer_id = 0
        try:
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
                                                    creation_user = request.user,
                                                    modification_user = request.user
                                                    )
            customer_id = customer_save.id
        except ValueError:
            messages.error(request, 'Server error. Please contact to administrator!')
            return render(request, 'proyect/new.html')

        
        #  Se intenta obtener el responsable 
        try:
            # Intentamos obtener el objeto
            responsible = Responsible.objects.get(id=responsible_id),
        except Responsible.DoesNotExist:
            # Si no existe, devolvemos None (equivalente a null en otros lenguajes)
            responsible = None


        #Se guarda los datos del proyecto
        proyect_id = 0        

        try:
            if int(type_id) and int(customer_id):
                proyect_save = Proyect.objects.create(  type=Type.objects.get(id=type_id), 
                                                        customer=Customer.objects.get(id=customer_id), 
                                                        responsible=responsible,
                                                        state=State.objects.get(id=state_Id),
                                                        date=date, 
                                                        description=proyect_description,
                                                        creation_user = request.user,
                                                        modification_user = request.user)
                proyect_id = proyect_save.id


                for decorator_id in decorators_ids:
                    decorator = Decorator.objects.get(id = decorator_id)
                    proyect = Proyect.objects.get(id = proyect_id)
                    decorator.proyects.add(proyect)

                for decorator_id in ascociate_ids:
                    decorator = Decorator.objects.get(id = decorator_id)
                    proyect = Proyect.objects.get(id = proyect_id)
                    decorator.proyects.add(proyect)


                Event.objects.create( type_event_id=1,                                        
                                        proyect_id=proyect_id, 
                                        user=request.user)
        
                return redirect(reverse('view_url', kwargs={'proyect_id': proyect_id}))

        except ValueError:        
            messages.error(request, 'Server error. Please contact to administrator!')
            return render(request, 'proyect/new.html')
                                      
    else:

        types = Type.objects.filter(status=1).order_by('id')
        decorators = Decorator.objects.filter(is_supervisor=1).order_by('name')
        responsibles = Responsible.objects.filter(status=1).order_by('name')


        type_select = Type.objects.first()
        responsable_select = -1

        return render(request, 'proyect/new.html', 
                    {'types': types,
                    'type_select': type_select,
                    'decorators': decorators,
                    'responsibles': responsibles,
                    'responsable_select': responsable_select,})


@login_required
def proyect_view(request, proyect_id):
    
    proyect = Proyect.objects.get(id = proyect_id) #obtiene solo un resultado
    customer = proyect.customer
    category = Category.objects.all().order_by('name')
    subcategory = Subcategory.objects.all().order_by('name')
    place = Place.objects.all().order_by('name')
    catalog = Catalog.objects.all().order_by('name')
        
    try:
        decorators = Decorator.objects.filter(proyects = proyect).order_by('name')
        events = Event.objects.filter(proyect_id = proyect_id).order_by('creation_date')

    except Decorator.DoesNotExist:
        decorators = None

    except Event.DoesNotExist:        
        events = None
                        
    return render(request, 'proyect/view.html',{'proyect': proyect,
                                                'customer': customer,
                                                'decorators': decorators,
                                                'events':events,
                                                'categories':category,
                                                'subcategories':subcategory,
                                                'places': place,
                                                'catalogs': catalog})  

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
     
    print("Valores recibidos: ", selected_values)

    decorators = Decorator.objects.filter(id__in =selected_values)    
        
    # Creamos una lista con los datos de cada proyecto
    decoratorsHTML = '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-6 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
    decoratorsHTML += '<th title="Field #1">Name</th>'
    decoratorsHTML += '<th title="Field #2">Email</th>'
    decoratorsHTML += '<th title="Field #3">Phone</th>'
    decoratorsHTML += '<th title="Field #4">Address</th>'
    decoratorsHTML += '<th title="Field #5">Apartment</th>'
    decoratorsHTML += '<th title="Field #6">City</th>'
    decoratorsHTML += '<th title="Field #7">State</th>'
    decoratorsHTML += '<th title="Field #8">Zipcode</th>'
    
    decoratorsHTML += '</tr></thead><tbody>'

    for decorator in decorators:  
        decoratorsHTML += '<tr>'
        decoratorsHTML += '<td>' + decorator.name + '</td>'
        decoratorsHTML += '<td>' + decorator.email + '</td>'
        decoratorsHTML += '<td>' + decorator.phone + '</td>'
        decoratorsHTML += '<td>' + decorator.address + '</td>'
        decoratorsHTML += '<td>' + decorator.apartment + '</td>'
        decoratorsHTML += '<td>' + decorator.city + '</td>'
        decoratorsHTML += '<td>' + decorator.state + '</td>'
        decoratorsHTML += '<td>' + decorator.zipcode + '</td>'        
        decoratorsHTML += '</tr>'
    
    decoratorsHTML += '</tbody></table>'
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


@login_required
def getAddress(request):

    condiciones = Q()

    if request.method == 'POST':       

        address = request.POST.get('address')        

        if address != '':            
            condiciones &= Q(address = address)        

    customer_data = funct_data_customer(condiciones) 
    messageHtml = ""
    
    if len(customer_data) > 0:

        # Creamos una lista con los datos de cada proyecto
        messageHtml = '<br/><div class="alert alert-warning d-flex align-items-center p-5"><div class="d-flex flex-column"><span><b>Note:</b> There is already a project for that address.</span></div></div>'
        
        messageHtml += '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-6 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
        messageHtml += '<th title="Field #1">Client</th>'
        messageHtml += '<th title="Field #2">Address</th>'
        messageHtml += '<th title="Field #3">Apartment</th>'
        messageHtml += '<th title="Field #4">City</th>'
        messageHtml += '<th title="Field #5">State</th>'
        messageHtml += '<th title="Field #6">ZIP code</th>'
        messageHtml += '<th title="Field #7"></th>'
        messageHtml += '</tr></thead><tbody>'

        for customer in customer_data:          
            messageHtml += '<tr>'
            messageHtml += '<td>' + customer['customerName'] + '</td>'
            messageHtml += '<td>' + customer['address'] + '</td>'
            messageHtml += '<td>' + customer['apartment'] + '</td>'
            messageHtml += '<td>' + customer['city'] + '</td>'
            messageHtml += '<td>' + customer['state_u'] + '</td>'
            messageHtml += '<td>' + customer['zipcode'] + '</td>'
            messageHtml += '<td><a href="../view/' + customer['id_proyect'] + '" class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm me-1"><span class="svg-icon svg-icon-3"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.3" d="M21.4 8.35303L19.241 10.511L13.485 4.755L15.643 2.59595C16.0248 2.21423 16.5426 1.99988 17.0825 1.99988C17.6224 1.99988 18.1402 2.21423 18.522 2.59595L21.4 5.474C21.7817 5.85581 21.9962 6.37355 21.9962 6.91345C21.9962 7.45335 21.7817 7.97122 21.4 8.35303ZM3.68699 21.932L9.88699 19.865L4.13099 14.109L2.06399 20.309C1.98815 20.5354 1.97703 20.7787 2.03189 21.0111C2.08674 21.2436 2.2054 21.4561 2.37449 21.6248C2.54359 21.7934 2.75641 21.9115 2.989 21.9658C3.22158 22.0201 3.4647 22.0084 3.69099 21.932H3.68699Z" fill="black" /><path d="M5.574 21.3L3.692 21.928C3.46591 22.0032 3.22334 22.0141 2.99144 21.9594C2.75954 21.9046 2.54744 21.7864 2.3789 21.6179C2.21036 21.4495 2.09202 21.2375 2.03711 21.0056C1.9822 20.7737 1.99289 20.5312 2.06799 20.3051L2.696 18.422L5.574 21.3ZM4.13499 14.105L9.891 19.861L19.245 10.507L13.489 4.75098L4.13499 14.105Z" fill="black" /></svg></span></a></td>'
            messageHtml += '</tr>'
    
        messageHtml += '</tbody></table>'
        messageHtml += ''
    
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': messageHtml})



############################
### Combos dependientes  ###
############################

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
        print("Valores recibidos: ", decorator.id )
        decoratorsHTML += '<option value=' + str(decorator.id) + '>' + decorator.name + '</option>'
                    
    # Devolvemos la lista de ascociates como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})


############################
######### Funciones ########
############################

def funct_data_proyect(filters):

    proyects_data = []

    if filters is None:
        proyects = Proyect.objects.all().order_by('-id')
    else:
        proyects = Proyect.objects.filter(filters).order_by('-id')


    # Creamos una lista con los datos de cada proyecto
    
    fecha_actual = datetime.now()

    for proyect in proyects:

        parsed_date = ''
        allDay = False

        try:
            if len(proyect.date) == 17:
                parsed_date = proyect.date
                parsed_date = str(datetime.strptime(parsed_date, "%Y-%m-%d, %H:%M"))
            
            elif len(proyect.date) == 10:            
                allDay = True
                parsed_date = str(datetime.strptime(proyect.date + ', 00:00', "%Y-%m-%d, %H:%M"))
            else:
                parsed_date = '1900-01-01, 00:00'    
                
        except ValueError:
            parsed_date = '1900-01-01, 00:00'
        
        
        decorators = Decorator.objects.filter(proyects = proyect).order_by('name')
        decoratorsStr = ''

        for decorator in decorators:              
            decoratorsStr += decorator.name + ' '


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
            'date': parsed_date,
            'creationDate': fecha_creacion.strftime("%Y-%m-%d"),
            'email': proyect.customer.email,
            'state_id': proyect.state.id,
            'state': proyect.state.name,
            'allDay': allDay,
            'difference': difference.days,
            'decorators': decoratorsStr,
        })
    
    return proyects_data
    

def funct_data_customer(filters):

    customer_data = []

    if filters is None:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(filters)

    # Creamos una lista con los datos de cada proyecto
    for customer in customers:      
        
        proyects = Proyect.objects.filter(customer = customer)
        proyectId = ''

        for proyect in proyects:              
            proyectId = str(proyect.id)
                
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
            'user_id': event.user_id,
            'creation_date': event.creation_date
        })
    
    return event_data