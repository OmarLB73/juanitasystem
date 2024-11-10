from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Type, Responsible, Customer, Proyect, State

admin.site.register(Type)
admin.site.register(Responsible)
admin.site.register(Customer)
admin.site.register(Proyect)
admin.site.register(State)

