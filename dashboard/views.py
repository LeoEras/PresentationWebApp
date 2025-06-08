from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    print(request.user)
    return render(request, "dashboard/home.html")