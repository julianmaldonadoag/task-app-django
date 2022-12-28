from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    else:
        username = request.POST['username']
        pwd1 = request.POST['password1']
        pwd2 = request.POST['password2']

        if pwd1 == pwd2:
            try:
                user = User.objects.create_user(username=username, password=pwd1)
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'User already exists'
                })
        else:
            return render(request, 'signup.html', {
                'form': UserCreationForm(),
                'error': 'Password do not match'
            })
        
def tasks(request):
    return render(request, 'tasks.html')
