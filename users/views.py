# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Bienvenido de nuevo!')
                return redirect('home')  # Redirigir a la página principal (o donde desees)
            else:
                messages.error(request, 'Credenciales inválidas. Por favor, intente nuevamente.')
        else:
            print(form.errors)  # Esto es solo para depurar
            messages.error(request, 'Formulario no válido. Por favor, revise los datos.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
