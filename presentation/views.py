from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Presentation, Slide
from .forms import PresentationUploadForm
from .utils import handle_uploaded_presentation
from django.contrib import messages
import os

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
            result = handle_uploaded_presentation(filename, pdf_file, request.user.username)

            presentation = form.save(commit=False)
            presentation.user = request.user
            presentation.pdf_file = result["pdf_path"]
            presentation.num_pages = result["num_pages"]
            presentation.thumbnail = os.path.join(result["images_folder"], result["image_files"][0])
            presentation.save()

            # Saving the slides images
            for idx, image_file in enumerate(result["image_files"], start=1):
                slide = Slide.objects.create(
                    presentation=presentation,
                    page_number=idx,
                    image_path=os.path.join(result["images_folder"], image_file),
                    contrast_score=result["contrast_values"][idx - 1]
                )
                slide.save()
            
            messages.success(request, "Presentation uploaded successfully!")
            return redirect("presentation:home")
    else:
        form = PresentationUploadForm()
    return render(request, "presentation/upload.html", {"form": form})

@login_required
def presentation_detail(request):
    pass