# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse
# import datetime

# def index(request):
#     now = datetime.datetime.now()
#     html = " <html><body><h1>'Hello, world'</h1></br> It is now %s .</body></html> " % now
#     return HttpResponse(html)

from django.shortcuts import render, redirect

# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from proyect.models import Usuario
from django.views.decorators.http import require_POST



def login_view(request):    
    return render(request, 'accounts/login.html')

@require_POST
def validate_username(request):

    email_get = request.POST.get('email', '')
    pass_get = request.POST.get('password', '')    

    if Usuario.objects.filter(email=email_get).exists():
        if Usuario.objects.filter(email=email_get).filter(password=pass_get).exists():
            #return redirect(dashboard_view)
            return JsonResponse({'is_valid': True, 'message': 'You have successfully logged in!', 'redirect_url': '/dashboard/'})
        else:
            return JsonResponse({'is_valid': False, 'message': 'Your password is not valid.', 'redirect_url': ''})
    else:
        return JsonResponse({'is_valid': False, 'message': 'Your email is not valid.', 'redirect_url': ''})

def dashboard_view(request):    
    return render(request, 'dashboard.html')

def proyect_view(request):    
    return render(request, 'proyect.html')
