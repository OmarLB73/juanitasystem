from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required #para controlar las sesiones
from django.db.models import Q, Count # permite realizar consultas complejas / Count permite agrupar consultas
from datetime import datetime # dar formato a la fecha

from ..models import Type, State, ProyectDecorator, UIElement, Proyect, Category, Place, Customer
from ..services.proyect_service import getDataProyect, getDataWOs, getCustomer
from ..utils.utils import htmlDataLog, getDecoratorsTable, getResumenWOs, newWO, saveEvent
from ..utils.pdf_utils import generate_pdf


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


    timeline = htmlDataLog(request)
    
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
                                                  'timeline': timeline,
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
        customer_data = getCustomer(condicionesCustomer, 1)

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

                    saveEvent(request, 1, proyect_save, None, None, 'Create')
                    newWO(request, proyect_id)                    

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


@login_required
def pdf_view(request, workorderId):

    response = generate_pdf(request, workorderId)
    return response


