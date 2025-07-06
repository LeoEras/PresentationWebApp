from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Presentation

# Create your views here.
@login_required
def home(request):
    presentations = Presentation.objects.filter(user=request.user)
    return render(request, "presentation/home.html", {
        "presentations": presentations,
    })