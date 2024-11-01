from django.db import models

# Create your models here.

class Perfil(models.Model):
    perfil_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)    
    estado = models.IntegerField(default=1)    
    usuario_creacion = models.CharField(max_length=50, default='admin')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    usuario_modificacion = models.CharField(max_length=50, default='admin')
    fecha_modificacion = models.DateTimeField(auto_now_add=True, null=True)

  #La clase Meta, ayuda a evitar usar prefijos de la aplicacion en la base de datos. 
    # Pero por un tema de orden, no la usaremos.
    #class Meta:
    #   db_table = 'perfiles'

    #Esto sirve para el shell, retorna la estructura definida
    def __str__(self):
        return f'{self.perfil_id} - {self.nombre}'

class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, default=3)
    estado = models.IntegerField(default=1)    
    usuario_creacion = models.CharField(max_length=50, default='admin')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    usuario_modificacion = models.CharField(max_length=50, default='admin')
    fecha_modificacion = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.usuario_id} - {self.email[:50]} - {self.perfil_id}'
    
    