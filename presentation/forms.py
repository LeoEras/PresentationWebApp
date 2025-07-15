from django import forms
from .models import Presentation
from pypdf import PdfReader

class PresentationUploadForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'pdf_file']
        widgets = {
            'pdf_file': forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
        }
    
    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
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