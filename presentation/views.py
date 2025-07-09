from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Presentation
from .forms import PresentationUploadForm
from .utils import file_handler

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
    if request.method == "POST":
        form = PresentationUploadForm(request.POST, request.FILES)
        if form.is_valid():
            filename = form.cleaned_data["title"]
            pdf_file = form.cleaned_data["pdf_file"]
            file_handler(filename, pdf_file, request.user.username)
            return redirect("presentation:home")
    else:
        form = PresentationUploadForm()
    return render(request, "presentation/upload.html", {"form": form})

@login_required
def presentation_detail(request):
    pass