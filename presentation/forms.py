from django import forms
from .models import Presentation
from pypdf import PdfReader
from django.core.validators import RegexValidator

class PresentationUploadForm(forms.ModelForm):
    title = forms.CharField(
        max_length=80,
        min_length=10,
        label="Title (between 10 and 80 characters)",
        validators=[
            RegexValidator(
                regex=r'^[\w\s\-.,()]+$',
                message="Title must contain only letters, numbers, spaces, and - _ . , ( )"
            )
        ]
    )

    class Meta:
        model = Presentation
        fields = ['title', 'pdf_file']
        widgets = {
            'pdf_file': forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty or whitespace.")
        return title
    
    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if file.content_type != 'application/pdf':
            raise forms.ValidationError("File is not recognized as a PDF.")
        if file.size == 0:
            raise forms.ValidationError("The file is empty.")
        if not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("The file is too large (max 5 MB).")
        try:
            pdf = PdfReader(file)
            if len(pdf.pages) == 0:
                raise forms.ValidationError("The PDF has no pages.")
        except Exception:
            raise forms.ValidationError("The uploaded file is not a valid PDF.")
        
        file.seek(0)
        return file