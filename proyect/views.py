from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib import messages
from datetime import datetime # dar formato a la fecha
from django.shortcuts import redirect # redireccionar a páginas
from django.contrib.auth.decorators import login_required #para controlar las sesiones


from .models import Type, Responsible, Customer, State, Proyect #Aquí importamos a los modelos que necesitamos

@login_required
def panel_view(request):

    #Consulta los proyectos desde la base de datos
    proyects = Proyect.objects.all()

    # Creamos una lista con los datos de cada proyecto
    proyects_data = []
    for proyect in proyects:

        parsed_date = ''
        allDay = False

        if len(proyect.date) == 10:
            allDay = True
            try:
                parsed_date = proyect.date + ', 00:00'
            except ValueError:
                parsed_date = '1900-01-01, 00:00'
        else:
            parsed_date = proyect.date

        proyects_data.append({
            'id': proyect.id,
            'customerName': proyect.customer.name,
            'address': proyect.customer.address,
            'date': datetime.strptime(parsed_date, "%Y-%m-%d, %H:%M"),
            'creationDate': proyect.creation_date,
            'email': proyect.customer.email,
            'state': proyect.state.name,
            'allDay': allDay,
        })

    return render(request, 'proyect/panel.html', {'proyects_data': proyects_data,})    


@login_required
def grafics_view(request):
    return render(request, 'proyect/grafics.html')    

@login_required
def proyect_new(request):
     
    if request.method == 'POST':
        
        type_id = request.POST.get('type')
        address = request.POST.get('address')
        customer_name = request.POST.get('customerName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        customer_Description = request.POST.get('customerDescription')
        customer_id = request.POST.get('customerId')        
        responsible_id = request.POST.get('responsible')        
        date = request.POST.get('date')
        proyectDescription = request.POST.get('proyectDescription')
        state_Id = 1 #Inicio        
        
        try:
            if int(customer_id):
                if Customer.objects.filter(id=customer_id).exists():
                    customer_save = Customer.objects.get(id=customer_id)
                    customer_save.name = customer_name
                    customer_save.email = email
                    customer_save.phone = phone
                    customer_save.description = customer_Description
                    customer_save.save()
        except ValueError:
            customer_save = Customer.objects.create(name=customer_name, address=address, email=email, phone=phone, description=customer_Description)
            customer_id = customer_save.id

        try:
            if int(type_id) and int(customer_id) and (responsible_id):
                Proyect.objects.create(type=Type.objects.get(id=type_id), 
                                       customer=Customer.objects.get(id=customer_id), 
                                       responsible=Responsible.objects.get(id=responsible_id),
                                       state=State.objects.get(id=state_Id),
                                       date=date, 
                                       description=proyectDescription)
                messages.success(request, 'Project saved successfully')
                return redirect('../../proyect/dashboard')

        except ValueError:
            Customer.objects.create(name=customer_name, address=address, email=email, phone=phone, description=customer_Description)
            messages.error(request, 'Server error. Please contact to administrator!')
            return render(request, 'proyect/new.html')
                                      
    else:

        types = Type.objects.filter(status=1)
        responsibles = Responsible.objects.filter(status=1)

        type_select = Type.objects.first()
        responsable_select = -1

        return render(request, 'proyect/new.html', 
                    {'types': types,
                    'type_select': type_select,
                    'responsibles': responsibles,
                    'responsable_select': responsable_select,})

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

        if len(proyect.date) == 10:
            allDay = True
            try:
                parsed_date = proyect.date + ', 00:00'
            except ValueError:
                parsed_date = '1900-01-01, 00:00'
        else:
            parsed_date = proyect.date

        proyects_data.append({
            'id': proyect.id,
            'name': proyect.customer.name,
            'address': proyect.customer.address,
            'date': datetime.strptime(parsed_date, "%Y-%m-%d, %H:%M"),
            'email': proyect.customer.email,
            'state': proyect.state.name,
            'allDay': allDay,
        })
    
    # Devolvemos la lista de proyectos como respuesta JSON
    return JsonResponse({'proyects': proyects_data})