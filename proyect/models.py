from django.db import models
from django.contrib.auth.models import User
import os #Para el tema del archivo
from django.utils import timezone #Para definir la ruta del archivo

from django.db.models.signals import pre_delete #Para borrar imagenes fisicas antes del borrado de la base de datos
from django.dispatch import receiver #Para borrar imagenes fisicas antes del borrado de la base de datos

from django.core.exceptions import PermissionDenied #Para no borrar registros

# Create your models here.


ESTADOS = [
        (1, 'Active'),
        (0, 'Inactive'),
    ]

YESNO = [
        (1, 'Yes'),
        (2, 'No'),
    ]

EVENTOS = [
        (0, 'Other'),
        (1, 'Create event'),
        (2, 'Comment'),
        (3, 'Create item'),
        (4, 'Delete item'),
        (5, 'Upload file/comment'),        
        (6, 'Change state'),
    ]


def getUploadTo(instance, filename):
    # Aquí se define la carpeta dinámica con base en el id del proyecto.
    model_name = instance.__class__.__name__ 

    if model_name in ('ItemImage','ItemMaterial','ItemFile'):
        proyectId = instance.item.workorder.proyect.id

    if model_name in ('ItemCommentStateFile'):
        proyectId = instance.item_comment_state.item.workorder.proyect.id

    if model_name in ('WorkOrderCommentStateFile'):
        proyectId = instance.workorder_comment_state.workorder.proyect.id


    return f"{model_name}/{proyectId}/{filename}"



class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    # created_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    #La clase Meta, ayuda a evitar usar prefijos de la aplicacion en la base de datos. 
    # Pero por un tema de orden, no la usaremos.
    # class Meta:
    #    db_table = 'Type'
    #Esto sirve para el shell, retorna la estructura definida
    
    def __str__(self):
        # return f'(ID:{self.id}) - {self.name}'
        return f'{self.name}'
    

class Responsible(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    color = models.CharField(max_length=10,null=True, blank=True)    
    id_user = models.IntegerField(default=0)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.email}'


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=500)
    apartment = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000, null=True, blank=True)
    notes = models.CharField(max_length=2000, null=True, blank=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.email}'
    

class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    buttonName = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name}'


class Proyect(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)    
    description = models.CharField(max_length=2000, null=True)
    code = models.CharField(max_length=50, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.customer.address} - {self.customer.name}'
    

class WorkOrder(models.Model):
    id = models.AutoField(primary_key=True)    
    proyect = models.ForeignKey(Proyect, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)        
    code = models.CharField(max_length=50, null=True)
    description = models.TextField(blank=True, null=True, max_length=2000)            
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)   
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.proyect.customer.address} - {self.proyect.customer.name}'


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=1)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name}'
    

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['name']  # Ordena por 'name' alfabéticamente por defecto

    def __str__(self):
        return f'{self.name} (Category: {self.category.name})'


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)           
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name}'


class ProyectDecorator(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    apartment = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000, null=True, blank=True)
    is_supervisor = models.IntegerField(choices=YESNO,  default=1)
    supervisor = models.ForeignKey(
        'self',  # 'self' hace referencia a esta misma clase
        on_delete=models.SET_NULL,  # Si se elimina la categoría padre, se establece como NULL
        null=True,  # Permitir categorías que no tengan categoría padre
        blank=True,  # Permitir que el campo esté vacío en el formulario
        related_name='assistant'  # El nombre de la relación inversa
    ) 
    proyects = models.ManyToManyField(
        Proyect,      
        blank=True,
        related_name='decoratorProyects')
    id_user = models.IntegerField(default=0)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.email}'
    

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    type_event_id = models.IntegerField(choices=EVENTOS,  default=0)
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=2000, null=True)    
    user  = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.name}'
      

class Attribute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    description = models.TextField(null=True, blank=True)    
    multiple = models.BooleanField(default=False)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)
   
    def __str__(self):
        return f'{self.name}'


class AttributeOption(models.Model):
    id = models.AutoField(primary_key=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)    
    description = models.TextField(null=True, blank=True)    
    file = models.ImageField(upload_to='attributes', blank=True, null=True)  # Nuevo campo de imagen
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)
   
    def __str__(self):
        return f'{self.name}'



class CategoryAttribute(models.Model):
    id = models.AutoField(primary_key=True)        
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)    
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.category.name} - {self.order} - {self.attribute.name}'


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)        
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    qty = models.TextField(blank=True, null=True, max_length=100)
    notes = models.TextField(blank=True, null=True, max_length=2000)
    date_proposed = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    responsible = models.ForeignKey(Responsible, on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):

        group_name = ''

        if self.group:
            group_name = self.group.name

        return f'{self.id} - {self.workorder.id} - {self.group.subcategory.category.name} - {self.group.subcategory.name} - {group_name}'
    

class ItemAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)        
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)    
    notes = models.CharField(blank=True, null=True, max_length=150)    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)   

    def __str__(self):
        return f'{self.id}'
    
class ItemAttributeNote(models.Model):
    id = models.AutoField(primary_key=True)
    itemattribute = models.ForeignKey(ItemAttribute, on_delete=models.CASCADE)
    attributeoption = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.id}'

#################################################################################################################################
#################################################################################################################################

# Clase base con atributos comunes
class ItemAttachment(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)    
    name = models.CharField(blank=True, null=True, max_length=150)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        abstract = True  # Esto hace que sea una clase base abstracta y no se cree una tabla para ella.

    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.name}'
    

class ItemImage(ItemAttachment):    
    file = models.ImageField(upload_to=getUploadTo, blank=True, null=True)  # Nuevo campo de imagen
    
    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.name}'
    

class ItemMaterial(ItemAttachment):
    file = models.ImageField(upload_to=getUploadTo, blank=True, null=True)  # Nuevo campo de imagen
    qty = models.CharField(blank=True, null=True, max_length=150)
    
    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.name}'


class ItemFile(ItemAttachment):    
    file = models.ImageField(upload_to=getUploadTo, blank=True, null=True)  # Nuevo campo de archivo    

    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.name}'
    

#################################################################################################################################
#################################################################################################################################
    
class ItemComment(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    type = models.IntegerField(choices=EVENTOS,  default=2)
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.notes}'
    

class ItemCommentState(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)    
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.notes}'


class ItemCommentStateFile(models.Model):
    id = models.AutoField(primary_key=True)
    item_comment_state = models.ForeignKey(ItemCommentState, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=getUploadTo, blank=True, null=True)  # Nuevo campo de archivo
    name = models.CharField(blank=True, null=True, max_length=150)
    creation_date = models.DateTimeField(default=timezone.now, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.name}'
    

class WorkOrderCommentState(models.Model):
    id = models.AutoField(primary_key=True)
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)    
    created_by_user = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True)
    modification_by_user = models.IntegerField(null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.proyect.id} - {self.notes}'


class WorkOrderCommentStateFile(models.Model):
    id = models.AutoField(primary_key=True)
    workorder_comment_state = models.ForeignKey(WorkOrderCommentState, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=getUploadTo, blank=True, null=True)  # Nuevo campo de archivo
    name = models.CharField(blank=True, null=True, max_length=150)
    creation_date = models.DateTimeField(default=timezone.now, null=True)
    
    def __str__(self):
        return f'{self.id} - {self.name}'
    


class UIElement(models.Model):
    key = models.CharField(max_length=100, unique=True)  # Un identificador único para cada etiqueta/título
    label_text = models.CharField(max_length=255, null=True, blank=True)  # El texto que representa la etiqueta o título
    language_code = models.CharField(max_length=10, default='en')  # El código de idioma, para soportar múltiples idiomas
    
    def __str__(self):
        return f'{self.id} - {self.key}'
    



def generalDelete(sender, instance, **kwargs):
    if instance.file:
        imagen_path = instance.file.path
        if os.path.isfile(imagen_path):
            os.remove(imagen_path)

@receiver(pre_delete, sender=ItemImage)
@receiver(pre_delete, sender=ItemMaterial)
@receiver(pre_delete, sender=ItemFile)
@receiver(pre_delete, sender=CategoryAttribute)
@receiver(pre_delete, sender=ItemCommentStateFile)
@receiver(pre_delete, sender=WorkOrderCommentStateFile)
def deleteFile(sender, instance, **kwargs):
    generalDelete(sender, instance, **kwargs)


