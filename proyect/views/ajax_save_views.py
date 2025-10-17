from django.contrib import messages
from django.http import JsonResponse # para responder llamadas Ajax
from django.contrib.auth.decorators import login_required #para controlar las sesiones

from datetime import datetime # dar formato a la fecha
from django.utils import timezone #Para ver la hora correctamente.

from PIL import Image #Para validar el tipo de imagen

from ..models import Group, Place, WorkOrder, Item, Subcategory, CategoryAttribute, ItemAttribute, ItemAttributeNote, Attribute, AttributeOption, ItemMaterial, ItemFile, ItemImage, ItemCommentState, ItemCommentStateFile,WorkOrderCommentState, WorkOrderCommentStateFile, Responsible, CalendarItem,CalendarWorkOrder, CalendarTask, State, Category
from ..services.proyect_service import saveCalendarItems, saveCalendarComments
from ..utils.utils import validateTypeFile, saveEvent, sendEmail




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


    
        subCategory = None
        if subcategory_id.isdigit(): # Si es numero, se asume que la categoria existe
            subCategory = Subcategory.objects.get(id=int(subcategory_id))
        else:
            
            category_input = request.POST.get('category')

            if category_input.isdigit():
                category = Category.objects.get(id=int(category_input))
            else:
                # Es un nuevo nombre: verificar si ya existe, o crearlo
                category, created = Category.objects.get_or_create(name=category_input)

                if created:
                    category.order = 2
                    category.created_by_user = request.user.id
                    category.modification_by_user = request.user.id
                    category.save()
                                                                                                     
            subCategory, created = Subcategory.objects.get_or_create(name=subcategory_id, category = category) # created=True si el objeto fue creado

            if created:
                subCategory.created_by_user = request.user.id
                subCategory.modification_by_user = request.user.id
                subCategory.save()



        group = None
        if group_id and group_id != '':
            if group_id.isdigit():
                if Group.objects.filter(id=group_id):
                    group = Group.objects.get(id=group_id)
            else:
                group, created = Group.objects.get_or_create(name=group_id, subcategory=subCategory)

                if created:
                    group.created_by_user = request.user.id
                    group.modification_by_user = request.user.id
                    group.save()

        place = None
        if place_id and place_id != '':
            if place_id.isdigit():
                if Place.objects.get(id=place_id):
                    place = Place.objects.get(id=place_id)
            else:
                place, created = Place.objects.get_or_create(name=place_id)

                if created:
                    place.created_by_user = request.user.id
                    place.modification_by_user = request.user.id
                    place.save()
        
        if item_id == '':
            item_id = 0

            
        try: 

            workorder = WorkOrder.objects.get(id=workorder_id)
            item = Item.objects.filter(workorder = workorder, id=item_id).first() #No siempre estará, por eso no se usa get

            if item:
                item_id = item.id
                
                item.subcategory = subCategory
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
                                            subcategory = subCategory,
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
        chkState = request.POST.get('chkState')
        date_end = request.POST.get('date_end')
        responsible_id = request.POST.get('responsable')        

        workorder = WorkOrder.objects.get(id=workOrderId)
        item = Item.objects.filter(workorder = workorder, id=itemId).first() #No siempre estará, por eso no se usa get
        accept = False

        if chkState:
            if chkState == 'on':
                accept = True

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
                                                                    accepted = accept,
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
                                                                            accepted = accept,
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
                dateStartHour_get = ' 00:00' 

            if dateEndHour_get == '' or dateEndHour_get == None:
                dateEndHour_get = ' 23:59' 

            if checkAllDay:
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


#Consulta ejecutada en el panel, para acceder a la info del proyecto.
@login_required
def saveSessionState(request):
    #Consulta los items desde la base de datos    
    stateId = request.POST.get('s')    
    request.session['stateId'] = stateId

    return JsonResponse({'result': 'OK'})



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


        if workOrder.state.id:

            enviado = sendEmail(
            destinatario= request.user.email,
            asunto= workOrder.state.name + ': ' + workOrder.proyect.customer.address,
            mensaje='Este es un mensaje de email desde el sistema de Juanita.'
        )



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

