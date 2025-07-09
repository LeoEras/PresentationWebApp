import os
from django.conf import settings

def file_handler(filename, pdf_file, username):
    path = os.path.join(settings.MEDIA_ROOT, "uploads/" + username + "/", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path + ".pdf", "wb+") as destination:
        for chunk in pdf_file.chunks():
            destination.write(chunk)