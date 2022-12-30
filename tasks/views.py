from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task

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

        if username == '' or pwd1 == '' or pwd2 == '':
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html', {
                'form': UserCreationForm()
            })
        if pwd1 == pwd2:
            try:
                user = User.objects.create_user(username=username, password=pwd1)
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                messages.error(request, 'User already exists.')
                return render(request, 'signup.html', {
                    'form': UserCreationForm()
                })
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html', {
                'form': UserCreationForm()
            })

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Username or password is incorrect.')
            return render(request, 'signin.html', {
                'form': AuthenticationForm()
            })
        else:
            login(request, user)
            return redirect('tasks')

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-created')
    return render(request, 'tasks.html', { 'tasks': tasks, 'completed': False })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False)
    return render(request, 'tasks.html', { 'tasks': tasks, 'completed': True })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', { 'task': task, 'form': form })
    # Update task.
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            messages.success(request, 'Task updated succesfully.')
            if task.datecompleted is None:
                return redirect('tasks')
            else:
                return redirect('tasks_completed')
        except ValueError:
            messages.error(request, 'Error updating task.')
            return render(request, 'task_detail.html', { 
                'task': task, 
                'form': form
            })

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm()
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            messages.success(request, 'Task added succesfully.')
            return redirect('tasks')
        except ValueError:
            messages.error(request, 'Please provide valid data.')
            return render(request, 'create_task.html', {
                'form': TaskForm()
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def undone_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = None
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')