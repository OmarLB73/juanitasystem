from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Type, Responsible, Customer, Proyect, State, Category, Subcategory, Decorator, Place, Attribute, Category_Attribute

admin.site.register(Type)
admin.site.register(Responsible)
admin.site.register(Customer)
admin.site.register(Proyect)
admin.site.register(State)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Decorator)
admin.site.register(Place)
admin.site.register(Attribute)
admin.site.register(Category_Attribute)


