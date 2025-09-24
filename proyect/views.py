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


from django.utils import timezone #Para ver la hora correctamente.



from django.http import HttpRequest #Para las sesiones

from django.contrib.auth.models import User #Datos del usuario
from .models import Type, Responsible, Customer, State, Proyect, ProyectDecorator, Event, Category, Subcategory, Place, CategoryAttribute, Attribute, Item, ItemAttribute, ItemImage, Group, ItemFile, ItemCommentState, ItemCommentStateFile, WorkOrder, ItemMaterial, WorkOrderCommentState, WorkOrderCommentStateFile, UIElement, AttributeOption, ItemAttributeNote, CalendarItem, CalendarWorkOrder, CalendarItemComment, CalendarItemCommentFile, CalendarWorkOrderComment, CalendarWorkOrderCommentFile, CalendarTask, CalendarTaskComment, CalendarTaskCommentFile #Aquí importamos a los modelos que necesitamos

import ast #Usado para pasar una lista string a lista de verdad


       
