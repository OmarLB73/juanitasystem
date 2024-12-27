from django.db import models
from django.contrib.auth.models import User
import os #Para el tema del archivo
from django.utils import timezone #Para definir la ruta del archivo

from django.db.models.signals import pre_delete #Para borrar imagenes fisicas antes del borrado de la base de datos
from django.dispatch import receiver #Para borrar imagenes fisicas antes del borrado de la base de datos

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
    ]

class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(choices=ESTADOS,  default=1)        
    creation_user = models.CharField(max_length=50, default='admin')    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    #La clase Meta, ayuda a evitar usar prefijos de la aplicacion en la base de datos. 
    # Pero por un tema de orden, no la usaremos.
    # class Meta:
    #    db_table = 'Type'

    #Esto sirve para el shell, retorna la estructura definida

    def __str__(self):
        return f'{self.id} - {self.name}'
    

class Responsible(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    id_user = models.IntegerField(default=0)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name} - {self.email}'


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=500)
    apartment = models.CharField(max_length=150, null=True)
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)    
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000, null=True)
    notes = models.CharField(max_length=2000, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=0, related_name='customer_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=0, related_name='customer_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name} - {self.email}'
    

class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(choices=ESTADOS,  default=1)        
    creation_user = models.CharField(max_length=50, default='admin')    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Proyect(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    responsible = models.ForeignKey(Responsible, on_delete=models.SET_NULL, null=True, default=0)
    state = models.ForeignKey(State, on_delete=models.CASCADE)    
    date = models.CharField(max_length=50)        
    description = models.CharField(max_length=2000, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=0, related_name='proyect_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=0, related_name='proyect_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.customer.address} - {self.customer.name} - {self.date}'


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name}'
    

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)   
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name}'
    

class Decorator(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    apartment = models.CharField(max_length=150, null=True)
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000, null=True)
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
        related_name='proyects')
    id_user = models.IntegerField(default=0)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name} - {self.email}'
    

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    type_event_id = models.IntegerField(choices=EVENTOS,  default=0)
    proyect_id  = models.IntegerField()
    description = models.CharField(max_length=2000, null=True)    
    user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='event_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')    
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name}'
    

class Attribute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='attribute_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='attribute_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name}'


class Category_Attribute(models.Model):
    id = models.AutoField(primary_key=True)        
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='category_attribute_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='category_attribute_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.category.name} - {self.attribute.name}'


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    proyect = models.ForeignKey(Proyect, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    qty = models.IntegerField(null=True)
    notes = models.TextField(blank=True, null=True, max_length=2000)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='item_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='item_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.proyect.name} - {self.category.name} - {self.subcategory.name}'
    

class Item_Attribute(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)        
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)    
    notes = models.CharField(blank=True, null=True, max_length=150)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='item_attribute_creation_set')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)    
    modification_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1, related_name='item_attribute_modification_set')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id}'


def get_file_path_img(instance, filename):
    # Crear subcarpetas con el ID del objeto
    year = instance.creation_date.year
    month = instance.creation_date.month
    proyect_id = instance.item.proyect.id
    return os.path.join('images', str(year), str(month), str(proyect_id), filename)
    

class Item_Images(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=get_file_path_img, blank=True, null=True)  # Nuevo campo de imagen
    name = models.CharField(blank=True, null=True, max_length=150)
    notes = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True)

    def save(self, *args, **kwargs):
        # Si es la primera vez que se guarda el objeto, el ID aún no está disponible
        if not self.id:
            super().save(*args, **kwargs)  # Guarda primero para asignar el ID
        else:
            super().save(*args, **kwargs)  # Luego guarda con el ID correctamente asignado


    def __str__(self):
        return f'{self.id} - {self.item.id} - {self.imagen}'






@receiver(pre_delete, sender=Item_Images)
def eliminar_imagen(sender, instance, **kwargs):
    if instance.file:
        imagen_path = instance.file.path
        if os.path.isfile(imagen_path):
            os.remove(imagen_path)
