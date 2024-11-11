from django.conf import settings

#Para definir variales de entorno, sin necesidad de cargar en cada vista

def settings_variables(request):
    return {
        'API_KEY': settings.GOOGLE_API_KEY,
    }