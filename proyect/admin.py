from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User #Datos del usuario
from .models import Type, Responsible, Customer, Proyect, State, Category, Subcategory, ProyectDecorator, Place, Attribute, CategoryAttribute, Group, UIElement, WorkOrder, AttributeOption


class TypeAdmin(admin.ModelAdmin):
    list_display = ['name','status','modification_by_user_text','modification_date']
    fields = ['name','status']
    ordering = ['name']
    search_fields = ['name']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class ResponsibleAdmin(admin.ModelAdmin):
    list_display = ['name','email','color','status','modification_by_user_text','modification_date']
    fields = ['name','email','color','status']
    ordering = ['name']
    search_fields = ['name','email']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name','phone','email','address','apartment','city','state','zipcode','status','modification_by_user_text','modification_date']
    fields = ['name','phone','email','address','apartment','city','state','zipcode','description','notes','status']
    ordering = ['name']
    search_fields = ['name','phone','email','address','apartment','city','state','zipcode','description','notes']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class StateAdmin(admin.ModelAdmin):
    list_display = ['id','name','buttonName','description','buttonDescription', 'linkDescription', 'modalTitle','modalSubTitle','positiveMessage','negativeMessage','status','modification_by_user_text','modification_date']
    fields = ['name','buttonName','description','buttonDescription','linkDescription','modalTitle','modalSubTitle','positiveMessage','negativeMessage','status']
    ordering = ['id']
    search_fields = ['name','buttonName','description','buttonDescription','linkDescription']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class ProyectAdmin(admin.ModelAdmin):
    list_display = ['type','customer','code','status','modification_by_user_text','modification_date']
    fields = ['type','customer','code','status']
    ordering = ['customer']
    search_fields = ['type','customer','code']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class CategoryAdmin(admin.ModelAdmin):    
    list_display = ['name','order','status','modification_by_user_text','modification_date']
    fields = ['order','name','status']
    ordering = ['order','name'] # Ordenar por el campo 'name' de forma ascendente (alfabéticamente)
    search_fields = ['name']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()
    

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name','order','name','status','modification_by_user_text','modification_date']
    fields = ['category','order','name','status']
    ordering = ['category','order','name']
    search_fields = ['name', 'category__name']

    # Método para mostrar el nombre de la categoría
    def category_name(self, obj):
        return obj.category.name if obj.category else "No Category"
    category_name.short_description = 'Category'

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()



class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_name', 'subcategory_name','status','modification_by_user_text','modification_date')
    # Aquí definas específicamente los campos que quieres que aparezcan en el formulario
    fields = ('subcategory', 'order','name','status')  # Excluyendo 'status' y 'order'
    ordering = ['subcategory__category__name', 'subcategory__name']
    list_filter = ('subcategory',)
    search_fields = ['name', 'subcategory__name', 'subcategory__category__name']

    readonly_fields = ('category_name', 'subcategory_name')  # Solo lectura para estos campos calculados

    
    
    def category_name(self, obj):
        return obj.subcategory.category.name
    category_name.admin_order_field = 'subcategory__category__name'

    def subcategory_name(self, obj):
        return obj.subcategory.name
    subcategory_name.admin_order_field = 'subcategory__name'


    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class ProyectDecoratorAdmin(admin.ModelAdmin):
    list_display = ['name','phone','address','apartment','city','state','zipcode','supervisor','status','modification_by_user_text','modification_date']
    fields = ['name','phone','email','address','apartment','city','state','zipcode','is_supervisor','supervisor','status']
    ordering = ['name']
    search_fields = ['name','email','phone','address','apartment','city','state','zipcode','supervisor']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name','status','modification_by_user_text','modification_date']
    fields = ['name','status']
    ordering = ['name']
    search_fields = ['name']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name','description','multiple','status','modification_by_user_text','modification_date']
    fields = ['name','description','multiple','status']
    ordering = ['name']
    search_fields = ['name','description']

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()



class AttributeOptionAdmin(admin.ModelAdmin):
    list_display = ['attribute','name','description','file','status','modification_by_user_text','modification_date']
    fields = ['attribute','name','description','file','status']
    ordering = ['attribute','name']
    search_fields = ['name','description']

    # Sobrescribimos el campo 'attribute' para que solo se puedan seleccionar atributos con 'multiple=True'
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "attribute":
            # Filtramos los atributos para que solo muestre aquellos con multiple=True
            kwargs["queryset"] = Attribute.objects.filter(multiple=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()



class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ['category', 'order', 'attribute','status','modification_by_user_text','modification_date']
    fields = ['category', 'order', 'attribute', 'status']
    ordering = ['category', 'order', 'attribute']
    search_fields = ['category', 'order', 'attribute']    

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


class UIElementAdmin(admin.ModelAdmin):
    list_display = ['key','label_text']
    fields = ['key','label_text']
    ordering = ['key']
    search_fields = ['key','label_text']


class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['proyect_address','code','state_name','status','modification_by_user_text','modification_date']
    fields = ['proyect','state','status']
    #ordering = ['proyect_address','state__name']
    search_fields = ['proyect_address','code','state_name']

    def proyect_address(self, obj):
        return obj.proyect.customer.address
    proyect_address.admin_order_field = 'proyect__customer__address'

    def state_name(self, obj):
        return obj.state.name
    state_name.admin_order_field = 'state__name'

    def modification_by_user_text(self, obj):
        user = User.objects.filter(id=obj.modification_by_user).first()
        return user.username if user else "Unknown"        
    modification_by_user_text.short_description = 'Modification by user'

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()

    def save_model(self, request, obj, form, change):
        if obj.created_by_user == None:
            obj.created_by_user = request.user.id  # Asigna el usuario logueado
        if obj.modification_by_user == None:
            obj.modification_by_user = request.user.id  # Asigna el usuario logueado
        obj.save()


admin.site.register(Type, TypeAdmin)
admin.site.register(Responsible, ResponsibleAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Proyect, ProyectAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(ProyectDecorator, ProyectDecoratorAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(CategoryAttribute, CategoryAttributeAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(UIElement, UIElementAdmin)
admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(AttributeOption, AttributeOptionAdmin)


