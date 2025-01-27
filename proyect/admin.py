from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Type, Responsible, Customer, Proyect, State, Category, Subcategory, Decorator, Place, Attribute, Category_Attribute, Group


class TypeAdmin(admin.ModelAdmin):
    list_display = ['name','status','modification_by_user','modification_date']
    fields = ['name','status']
    ordering = ['name']
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()

class ResponsibleAdmin(admin.ModelAdmin):
    list_display = ['name','email','status','modification_by_user','modification_date']
    fields = ['name','email','status']
    ordering = ['name']
    search_fields = ['name','email']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name','phone','email','address','apartment','city','state','zipcode','status','modification_by_user','modification_date']
    fields = ['name','phone','email','address','apartment','city','state','zipcode','description','notes','status']
    ordering = ['name']
    search_fields = ['name','phone','email','address','apartment','city','state','zipcode','description','notes']


    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class StateAdmin(admin.ModelAdmin):
    list_display = ['name','status','modification_by_user','modification_date']
    fields = ['name','status']
    ordering = ['name']
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class ProyectAdmin(admin.ModelAdmin):
    list_display = ['type','customer','state','code','status','modification_by_user','modification_date']
    fields = ['type','customer','state','code','status']
    ordering = ['customer']
    search_fields = ['type','customer','state','code']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class CategoryAdmin(admin.ModelAdmin):    
    list_display = ['name','order','status','modification_by_user','modification_date']
    fields = ['order','name','status']
    ordering = ['order','name'] # Ordenar por el campo 'name' de forma ascendente (alfabéticamente)
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()
    

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['category','order','name','status','modification_by_user','modification_date']
    fields = ['category','order','name','status']
    ordering = ['category','order','name']
    search_fields = ['category','name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class GroupAdmin(admin.ModelAdmin):
    list_display = ['category','subcategory','order','name','status','modification_by_user','modification_date']
    fields = ['category','subcategory','order','name','status']
    ordering = ['category','subcategory','order','name']
    search_fields = ['category','subcategory','name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class DecoratorAdmin(admin.ModelAdmin):
    list_display = ['name','phone','address','apartment','city','state','zipcode','supervisor','status','modification_by_user','modification_date']
    fields = ['name','phone','email','address','apartment','city','state','zipcode','is_supervisor','supervisor','status']
    ordering = ['name']
    search_fields = ['name','email','phone','address','apartment','city','state','zipcode','supervisor']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name','status','modification_by_user','modification_date']
    fields = ['name','status']
    ordering = ['name']
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name','description','status','modification_by_user','modification_date']
    fields = ['name','description','status']
    ordering = ['name']
    search_fields = ['name','description']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


class Category_AttributeAdmin(admin.ModelAdmin):
    list_display = ['category', 'order', 'attribute','file','status','modification_by_user','modification_date']
    fields = ['category', 'order', 'attribute', 'file','status']
    ordering = ['category', 'order', 'attribute']
    search_fields = ['category', 'order', 'attribute']

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user  # Asigna el usuario logueado
        obj.save()


admin.site.register(Type, TypeAdmin)
admin.site.register(Responsible, ResponsibleAdmin)
admin.site.register(Customer, CustomerAdmin)
# admin.site.register(Proyect, ProyectAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Decorator, DecoratorAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Category_Attribute, Category_AttributeAdmin)
admin.site.register(Group, GroupAdmin)

