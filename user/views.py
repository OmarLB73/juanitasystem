# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse #Para responder por AJAX

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #messages.success(request, '¡Welcome to back!')
                return JsonResponse({'success': True, 'message': 'You have successfully logged in!', 'redirect_url': '../../proyect/dashboard'})
                
                #return redirect('/admin')  # Redirigir a la página principal (o donde desees)
            else:                
                return JsonResponse({'success': False, 'message': 'Invalid credentials. Please try again.', 'redirect_url': ''})            
                #messages.error(request, 'Credenciales inválidas. Por favor, intente nuevamente.')


        else:
            
            print(form.errors)  # Esto es solo para depurar
            return JsonResponse({'success': False, 'message': 'Invalid credentials. Please try again.', 'redirect_url': ''})
            
            
            # messages.error(request, 'Formulario no válido. Por favor, revise los datos.')
            
    else:
        form = AuthenticationForm()

    return render(request, 'user/login.html', {'form': form})