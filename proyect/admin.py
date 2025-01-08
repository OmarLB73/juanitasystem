from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Type, Responsible, Customer, Proyect, State, Category, Subcategory, Decorator, Place, Attribute, Category_Attribute

class CategoryAdmin(admin.ModelAdmin):
    # Ordenar por el campo 'name' de forma ascendente (alfabéticamente)
    ordering = ['order', 'name']

    # Opcional: Puedes agregar los campos que quieres mostrar en la lista del admin
    # list_display = ['nombre']

class SubcategoryAdmin(admin.ModelAdmin):
    ordering = ['category', 'order', 'name']

class AttributeAdmin(admin.ModelAdmin):
    ordering = ['name']

class Category_AttributeAdmin(admin.ModelAdmin):
    ordering = ['category', 'order', 'attribute']

class PlaceAdmin(admin.ModelAdmin):
    ordering = ['name']

class CustomerAdmin(admin.ModelAdmin):
    ordering = ['name']

class ResponsibleAdmin(admin.ModelAdmin):
    ordering = ['name']

class TypeAdmin(admin.ModelAdmin):
    ordering = ['name']

class DecoratorAdmin(admin.ModelAdmin):
    ordering = ['name']

class StateAdmin(admin.ModelAdmin):
    ordering = ['id']


admin.site.register(Type, TypeAdmin)
admin.site.register(Responsible, ResponsibleAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Proyect)
admin.site.register(State, StateAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Decorator, DecoratorAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Category_Attribute, Category_AttributeAdmin)


