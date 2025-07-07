from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .forms import LoginForm, RegistrationForm
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('presentation:home')

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('presentation:home')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "login/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('presentation:home')
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            repeat_password = form.cleaned_data["repeat_password"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
        
        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            form.add_error(None, "Username already exists.")
        
        if password != repeat_password:
            form.add_error(None, "Passwords do not match.")

        # Create a new user
        if not form.errors:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            login(request, user)
            messages.success(request, "Registration successful! Welcome, {}.".format(username))
            return redirect('presentation:home')
    else:
        form = RegistrationForm()
    
    return render(request, "login/register.html", {"form": form})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login:login_view')  # redirect to the login page URL