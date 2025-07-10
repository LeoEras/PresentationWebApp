from django.db import models
from django.contrib.auth.models import User

class Presentation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presentations')
    title = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='presentations/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    overall_rating = models.CharField(max_length=50, blank=True, null=True) 
    num_pages = models.PositiveIntegerField(default=0)
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('error', 'Error'),
        ],
        default='pending'
    )
    
    def __str__(self):
        return self.title
    
class Slide(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='slides')
    page_number = models.PositiveIntegerField()
    image_path = models.CharField(max_length=500, blank=True, null=True)
    words_score = models.FloatField(default=0)
    fonts_score = models.FloatField(default=0)
    contrast_score = models.FloatField(default=0)
    font_size_score = models.FloatField(default=0)

    def __str__(self):
        return f"Slide {self.page_number} of {self.presentation.title}"