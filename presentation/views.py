from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Presentation

# Create your views here.
@login_required
def home(request):
    presentations = Presentation.objects.filter(user=request.user).order_by('-upload_date')[:3]
    has_presentations = presentations.exists()
    return render(request, "presentation/home.html", {
        "presentations": presentations,
        "has_presentations": has_presentations,
    })

@login_required
def upload(request):
    pass

@login_required
def presentation_detail(request):
    pass