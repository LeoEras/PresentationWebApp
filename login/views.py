from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            # Successful login
            login(request, user)
            return redirect('dashboard:home')
        else:
            # Failed login
            return render(request, "login/login.html", {"error": "Invalid credentials"})
    return render(request, "login/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        repeat_password = request.POST.get("repeat_password")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        
        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            return render(request, "login/register.html", {"error": "Username already exists"})
        
        if password != repeat_password:
            return render(request, "login/register.html", {"error": "Passwords do not match"})

        # Create a new user
        user = User.objects.create_user(username=username, password=password, email=email, first_name = first_name, last_name = last_name)
        login(request, user)
        return redirect('dashboard:home')
    
    return render(request, "login/register.html")

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, "login/login.html")