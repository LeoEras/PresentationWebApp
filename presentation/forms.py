from django import forms
from .models import Presentation

class PresentationUploadForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'pdf_file']
    
    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        if file.size > 10 * 1024 * 1024:  # 10MB limit (optional)
            raise forms.ValidationError("The file is too large (max 10MB).")
        return file