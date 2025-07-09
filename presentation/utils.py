import os
import fitz
from django.conf import settings
import cv2
import numpy as np

def save_pdf(filename, pdf_file, username):
    output_folder = os.path.join(settings.MEDIA_ROOT, "uploads/" + username + "/" + filename + "/")
    pdf_path = os.path.join(output_folder, filename + ".pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(pdf_path, "wb+") as destination:
        for chunk in pdf_file.chunks():
            destination.write(chunk)

    relative_pdf_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
    relative_output_folder = os.path.relpath(output_folder, settings.MEDIA_ROOT)
    return relative_output_folder, relative_pdf_path

def pdf_to_images(relative_pdf_path, base_folder, filename, dpi=150):
    output_folder = os.path.join(settings.MEDIA_ROOT, base_folder, "images")
    os.makedirs(output_folder, exist_ok=True)
    pdf_real_path = os.path.join(settings.MEDIA_ROOT, relative_pdf_path)

    pdf_document = fitz.open(pdf_real_path)
    image_paths = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        pix = page.get_pixmap(dpi=dpi)
        
        output_path = os.path.join(
            output_folder, f"{filename}_{page_num + 1}.png"
        )
        pix.save(output_path)
        
        image_paths.append(f"{filename}_{page_num + 1}.png")
    
    relative_images_folder = os.path.relpath(output_folder, settings.MEDIA_ROOT)

    return relative_images_folder, image_paths, len(pdf_document)

def extract_text_boxes(pdf_path):
    pdf_document = fitz.open(pdf_path)

    pages_data = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text_boxes_per_page = []

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_boxes_per_page.append({
                            "text": span["text"],
                            "bbox": span["bbox"],
                            "font_size": span["size"],
                            "font": span["font"],
                        })

        page_data = {
            "page": page_num,
            "text_boxes": text_boxes_per_page
        }

        pages_data.append(page_data)
    return pages_data

def calculate_image_contrast(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    contrast = float(np.std(img))
    return contrast

def calculate_contrast(rel_pdf_path):
    full_pdf_path = os.path.join(settings.MEDIA_ROOT, rel_pdf_path)
    pages_data = extract_text_boxes(full_pdf_path)
    print(pages_data)

def handle_uploaded_presentation(filename, pdf_file, username):
    base_folder, rel_pdf_path = save_pdf(filename, pdf_file, username)
    images_folder, image_files, num_pages = pdf_to_images(rel_pdf_path, base_folder, filename)

    pages_data = calculate_contrast(rel_pdf_path)
    print(pages_data)
    # # Getting contrast values
    # contrast_values = []
    # for image_filename in image_files:
    #     image_full_path = os.path.join(settings.MEDIA_ROOT, images_folder, image_filename)
    #     contrast = calculate_image_contrast(image_full_path)
    #     contrast_values.append(contrast)

    return {
        "pdf_path": rel_pdf_path,
        "images_folder": images_folder,
        "image_files": image_files,
        "num_pages": num_pages,
       # "contrast_values": contrast_values,
    }