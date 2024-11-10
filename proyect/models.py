from django.db import models

# Create your models here.

class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(default=1)        
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
    email = models.CharField(max_length=100)
    id_user = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
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
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    description = models.CharField(max_length=2000)
    status = models.IntegerField(default=1)
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.name} - {self.email}'
    

class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)    
    status = models.IntegerField(default=1)        
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
    responsible = models.ForeignKey(Responsible, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)    
    date = models.CharField(max_length=50)        
    description = models.CharField(max_length=2000)
    status = models.IntegerField(default=1)
    creation_user = models.CharField(max_length=50, default='admin')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_user = models.CharField(max_length=50, default='admin')
    modification_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.customer.address} - {self.customer.name} - {self.date}'
