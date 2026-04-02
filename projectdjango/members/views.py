from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

def login_user(request):
    if request.method == "POST":
        password = request.POST.get("password", "")
        email = request.POST.get("email", "")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
        # Redirect to a success page.
            return redirect('home')
        else:
            messages.success(request,("Error Error"))
            return redirect('login')
    
    else:
        # Return an 'invalid login' error message.
    
        return render(request, 'authenticate/login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ("Logout successful"))
    return redirect('home')

from .forms import EmailUserCreationForm

def register_user(request):
    if request.method == "POST":
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login natively after creation without explicitly passing the username hook
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, ("Registation Complete"))
            return redirect('home')
    else:
        form = EmailUserCreationForm()

    return render(request, 'authenticate/register_user.html', {'form':form,})

def is_user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@login_required
def dashboard(request):
    if is_user_in_group(request.user, 'Admin'):
        return HttpResponse("Welcome, Admin!")
    elif is_user_in_group(request.user, 'Advisor'):
        return HttpResponse("Welcome, Advisor!")
    elif is_user_in_group(request.user, 'Student'):
        return HttpResponse("Welcome, Student!")
    else:
        return HttpResponse("You are not in any special group.")
    
def check_team_membership(request, target_id):
    # Get the AppUser profile
    app_user = request.user.app_profile

    user_teams = app_user.teams.all() 
    
    # Check if this ID exists in the user's teams
    is_in_team = app_user.teams.filter(name ="Team A").exists()

    if app_user.teams.filter(name="Team A").exists():
        print("User is in Alpha Squad")
    
    if is_in_team:
        print("User is in Team A")
        pass