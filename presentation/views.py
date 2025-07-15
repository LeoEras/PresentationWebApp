from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Presentation, Slide
from .forms import PresentationUploadForm
from .utils import handle_uploaded_presentation, feedback_from_words_score, feedback_from_contrast_score, feedback_from_fonts_size_score
from django.contrib import messages
import numpy as np
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

def calculate_score(slides):
    score_arr = []
    for slide in slides:
        score_arr.append(slide.overall_rating)

    average = round(np.average(score_arr).item(), 1)
    return average

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
                    contrast_score=result["contrast_scores"][idx - 1],
                    words_score=result["num_words_scores"][idx - 1],
                    font_size_score=result["font_size_score"][idx - 1],
                )
                slide.overall_rating = round(np.average([slide.contrast_score, slide.words_score, slide.font_size_score]).item(), 1)
                slide.save()
            
            slides = Slide.objects.filter(presentation=presentation)
            presentation.overall_rating = calculate_score(slides)
            presentation.save()
            
            messages.success(request, "Presentation uploaded successfully!")
            return redirect("presentation:home")
        else:
            return render(request, "presentation/upload.html", {"form": form})
    else:
        form = PresentationUploadForm()
    return render(request, "presentation/upload.html", {"form": form})


def build_feedback(slides):
    feedback_slide = []
    for slide in slides:
        feedback = ""
        feedback = feedback + feedback_from_contrast_score(slide.contrast_score) + "\n"
        feedback = feedback + feedback_from_words_score(slide.words_score) + "\n"
        feedback = feedback + feedback_from_fonts_size_score(slide.font_size_score) + "\n"
        feedback_slide.append(feedback)
    return feedback_slide

@login_required
def presentation_detail(request, pk):
    presentation = Presentation.objects.get(id=pk)
    slides = Slide.objects.filter(presentation=presentation)
    focused = slides[0]
    total = slides.count()
    feedback = build_feedback(slides)

    slides_arr = []
    for i in range(0, len(slides)):
        slide_dict = {}
        slide_dict["image_path"] = slides[i].image_path
        slide_dict["contrast_score"] = round(slides[i].contrast_score, 1)
        slide_dict["words_score"] = round(slides[i].words_score, 1)
        slide_dict["font_size_score"] = round(slides[i].font_size_score, 1)
        slide_dict["page_number"] = slides[i].page_number
        slide_dict["feedback"] = feedback[i]

        slides_arr.append(slide_dict)

    return render(request, "presentation/presentation.html", {
        "presentation": presentation,
        "focused": focused,
        "slides": slides_arr,
        "total_slides": total,
        "feedback": feedback,
    })