from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib import messages
from datetime import datetime # dar formato a la fecha
from django.shortcuts import redirect # redireccionar a páginas
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q # permite realizar consultas complejas
from django.urls import reverse #evita doble envio de formulario


from .models import Type, Responsible, Customer, State, Proyect, Decorator #Aquí importamos a los modelos que necesitamos

@login_required
def panel_view(request):

    #Consulta los proyectos/tipos/estados desde la base de datos    
    types = Type.objects.filter(status=1).order_by('id')
    states = State.objects.filter(status=1).order_by('id')

    type_id = 0
    state_id = 0
    date_from = ''
    date_until = ''

    proyects = Proyect.objects.all()

    if request.method == 'POST':

        condiciones = Q()

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

        proyects = Proyect.objects.filter(condiciones)

    else:
        proyects = Proyect.objects.all()
            

    # Creamos una lista con los datos de cada proyecto
    proyects_data = []
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
                    

        proyects_data.append({
            'id': proyect.id,
            'customerName': proyect.customer.name,
            'address': proyect.customer.address,
            'city': proyect.customer.city,
            'state_u': proyect.customer.state,
            'zipcode': proyect.customer.zipcode,
            'apartment': proyect.customer.apartment,
            'date': parsed_date,
            'creationDate': proyect.creation_date.strftime("%Y-%m-%d"),
            'email': proyect.customer.email,
            'state_id': proyect.state.id,
            'state': proyect.state.name,
            'allDay': allDay,            
        })

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
        
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        apartment = request.POST.get('apartment')
        
        customer_Description = request.POST.get('customerDescription')        
        customer_name = request.POST.get('customerName')

        email = request.POST.get('email')
        phone = request.POST.get('phone')

        date = request.POST.get('date')           
        responsible_id = request.POST.get('responsible')        
        proyectDescription = request.POST.get('proyectDescription')
        
        state_Id = 1 #Inicio


            #    if Customer.objects.filter(id=customer_id).exists():
            #         customer_save = Customer.objects.get(id=customer_id)
            #         customer_save.name = customer_name
            #         customer_save.email = email
            #         customer_save.phone = phone
            #         customer_save.description = customer_Description
            #         customer_save.save()

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
                                                    description=customer_Description)
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

        proyect_id = 0
        try:
            if int(type_id) and int(customer_id):
                customer_save = Proyect.objects.create( type=Type.objects.get(id=type_id), 
                                                        customer=Customer.objects.get(id=customer_id), 
                                                        responsible=responsible,
                                                        state=State.objects.get(id=state_Id),
                                                        date=date, 
                                                        description=proyectDescription)
                proyect_id = customer_save.id


                for decorator_id in decorators_ids:
                    decorator = Decorator.objects.get(id = decorator_id)
                    proyect = Proyect.objects.get(id = proyect_id)
                    decorator.proyects.add(proyect)

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
    return render(request, 'proyect/view.html')   


@login_required
def grafics_view(request):
    return render(request, 'proyect/grafics.html')    


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
    proyects = Proyect.objects.all()

    # Creamos una lista con los datos de cada proyecto
    proyects_data = []
    for proyect in proyects:

        parsed_date = ''
        allDay = False

        try:
            if len(proyect.date) == 17:
                parsed_date = str(datetime.strptime(proyect.date, "%Y-%m-%d, %H:%M"))
            
            elif len(proyect.date) == 10:            
                allDay = True
                parsed_date = str(datetime.strptime(proyect.date + ', 00:00', "%Y-%m-%d, %H:%M"))
            else:
                parsed_date = '1900-01-01, 00:00'    
                
        except ValueError:
            parsed_date = '1900-01-01, 00:00'

        proyects_data.append({
            'id': proyect.id,
            'name': proyect.customer.name,
            'address': proyect.customer.address,
            'date': parsed_date,
            'email': proyect.customer.email,
            'state': proyect.state.name,
            'allDay': allDay,
        })
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'proyects': proyects_data})


@login_required
def getDataDecorator(request):
    #Consulta los decoradores desde la base de datos
    selected_values_str = request.POST.get('decoratorsSelect')
    selected_values = selected_values_str.split(',')
    selected_values = [int(id_value) for id_value in selected_values]
     
    print("Valores recibidos: ", selected_values)

    decorators = Decorator.objects.filter(id__in =selected_values,is_supervisor=1)    
        
    # Creamos una lista con los datos de cada proyecto
    decoratorsHTML = '<table class="table table-row-bordered table-flush align-middle gy-6"><thead class="border-bottom border-gray-200 fs-6 fw-bolder bg-lighten"><tr class="fw-bolder text-muted">'
    decoratorsHTML += '<th title="Field #1">Name</th>'
    decoratorsHTML += '<th title="Field #2">Email</th>'
    decoratorsHTML += '<th title="Field #3">Phone</th>'
    decoratorsHTML += '<th title="Field #4">Address</th>'
    decoratorsHTML += '<th title="Field #5">City</th>'
    decoratorsHTML += '<th title="Field #6">State</th>'
    decoratorsHTML += '<th title="Field #7">Zipcode</th>'
    decoratorsHTML += '<th title="Field #8">Apartment</th>'    
    decoratorsHTML += '</tr></thead><tbody>'

    for decorator in decorators:  
        decoratorsHTML += '<tr>'
        decoratorsHTML += '<td>' + decorator.name + '</td>'
        decoratorsHTML += '<td>' + decorator.email + '</td>'
        decoratorsHTML += '<td>' + decorator.phone + '</td>'
        decoratorsHTML += '<td>' + decorator.address + '</td>'
        decoratorsHTML += '<td>' + decorator.city + '</td>'
        decoratorsHTML += '<td>' + decorator.state + '</td>'
        decoratorsHTML += '<td>' + decorator.zipcode + '</td>'
        decoratorsHTML += '<td>' + decorator.apartment + '</td>'        
        decoratorsHTML += '</tr>'
    
    decoratorsHTML += '</tbody></table>'
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'result': decoratorsHTML})