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
    text_content = models.TextField(blank=True, null=True)
    font_names = models.TextField(blank=True, null=True)
    avg_font_size = models.FloatField(blank=True, null=True)
    num_words = models.PositiveIntegerField(default=0)
    dominant_bg_color = models.CharField(max_length=20, blank=True, null=True)
    dominant_text_color = models.CharField(max_length=20, blank=True, null=True)
    contrast_ratio = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Slide {self.page_number} of {self.presentation.title}"