from django.db import models

# Create your models here.


ESTADOS = [
        (1, 'Active'),
        (0, 'Inactive'),
    ]

YESNO = [
        (1, 'Yes'),
        (2, 'No'),
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
    #class Meta:
    #   db_table = 'Type'

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
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)    
    apartment = models.CharField(max_length=150, null=True)    
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=2000, null=True)
    status = models.IntegerField(choices=ESTADOS,  default=1)
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
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
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
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
    city = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    zipcode = models.CharField(max_length=50, null=True)    
    apartment = models.CharField(max_length=150, null=True)    
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