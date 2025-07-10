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
        
        mat = fitz.Matrix(1, 1)
        pix = page.get_pixmap(matrix=mat)
        
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
            if block["type"] == 0: # Text data
                for line in block["lines"]:
                    for span in line["spans"]:
                        if len(span["text"]) == 1 and not span["text"].isalnum():
                            continue
                        if not span["text"].strip():
                            continue
                        if len(span["text"]) == 1 and span["text"].isdigit():
                            continue
                        if span["text"] == str(page_num + 1):
                            continue

                        text_boxes_per_page.append({
                            "text": span["text"].strip(),
                            "bbox": span["bbox"],
                            "font_size": span["size"],
                            "color": span["color"],
                            "font": span["font"],
                        })

        page_data = {
            "page": page_num + 1,
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

def is_bold_font(font_name):
    return 'bold' in font_name.lower()

def int_to_rgb(color_int):
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return (r, g, b)

def contrast_to_stars(contrast_ratio, font_size_pt, is_bold=False):
    if contrast_ratio < 5:
        stars = 1
    elif contrast_ratio < 8:
        stars = 2
    elif contrast_ratio < 14:
        stars = 3
    elif contrast_ratio < 18:
        stars = 4
    elif contrast_ratio <= 20:
        stars = 5
    else:
        stars = 5  # Just in case

    # Half star bonus for large text
    if (font_size_pt >= 18) or (is_bold and font_size_pt >= 14):
        stars += 0.5

    # Cap at 5 stars
    if stars > 5:
        stars = 5

    return stars

def calculate_num_words(pages_data):
    num_words_scores = []
    for data in pages_data:

        if len(data["text_boxes"]) == 0:
            num_words_scores.append(5)
            continue
        
        num_word_per_page = 0
        for t_box in data["text_boxes"]:
            num_word_per_page = num_word_per_page + len(t_box["text"].split(" "))
        
        num_words_scores.append(words_to_stars(num_word_per_page))
    return num_words_scores

def words_to_stars(num_words):
    if num_words <= 25:
        stars = 5
    elif num_words <= 40:
        stars = 4
    elif num_words <= 60:
        stars = 3
    elif num_words <= 80:
        stars = 2
    else:
        stars = 1
    return stars

def calculate_contrast(pages_data, images_folder, filename):
    contrasts_scores = []

    for data in pages_data:
        page = data["page"]
        image_filename = f"{filename}_{page }.png"
        image_full_path = os.path.join(settings.MEDIA_ROOT, images_folder, image_filename)
        
        img = cv2.imread(image_full_path)
        contrasts_per_page = []

        if len(data["text_boxes"]) == 0:
            contrasts_scores.append(5)
            continue
        
        for t_box in data["text_boxes"]:
            x0_px, y0_px, x1_px, y1_px = map(int, t_box["bbox"])
            font_size = t_box["font_size"]
            font_name = t_box["font"]
            bold = is_bold_font(font_name)

            # Text color extracted from PDF metadata, convert to RGB tuple
            text_color_rgb = int_to_rgb(t_box["color"])

            # Define padding around the text box for background sampling
            padding = 5
            height, width = img.shape[:2]

            # Calculate background crop coordinates with padding and clamp to image size
            x0_bg = max(x0_px - padding, 0)
            y0_bg = max(y0_px - padding, 0)
            x1_bg = min(x1_px + padding, width)
            y1_bg = min(y1_px + padding, height)

            # Crop the background region including padding
            bg_region = img[y0_bg:y1_bg, x0_bg:x1_bg].copy()

            # Mask out the text box itself from the background region (set to zero)
            text_x0_in_bg = x0_px - x0_bg
            text_y0_in_bg = y0_px - y0_bg
            text_x1_in_bg = x1_px - x0_bg
            text_y1_in_bg = y1_px - y0_bg

            bg_region[text_y0_in_bg:text_y1_in_bg, text_x0_in_bg:text_x1_in_bg] = 0

            # Create a mask to select pixels that are not zeroed out
            gray_bg = cv2.cvtColor(bg_region, cv2.COLOR_BGR2GRAY)
            mask = gray_bg > 0

            # Calculate average background color from masked pixels
            if mask.any():
                bg_pixels = bg_region[mask]
                bg_color_bgr = bg_pixels.mean(axis=0)
            else:
                bg_color_bgr = [255, 255, 255]  # fallback to white background

            # Convert background color from BGR (OpenCV default) to RGB
            bg_color_rgb = bg_color_bgr[::-1]

            # Luminance function based on sRGB luminance formula
            def luminance(rgb):
                R, G, B = [v / 255.0 for v in rgb]
                return 0.2126 * R + 0.7152 * G + 0.0722 * B

            # Compute luminance values for text and background
            lum_text = luminance(text_color_rgb)
            lum_bg = luminance(bg_color_rgb)

            # Calculate contrast ratio as per WCAG
            lighter = max(lum_text, lum_bg)
            darker = min(lum_text, lum_bg)
            contrast_ratio = (lighter + 0.05) / (darker + 0.05)
            contrasts_per_page.append(contrast_to_stars(contrast_ratio, font_size, bold))
        contrasts_scores.append(np.average(contrasts_per_page).item())
    return contrasts_scores

def handle_uploaded_presentation(filename, pdf_file, username):
    base_folder, rel_pdf_path = save_pdf(filename, pdf_file, username)
    images_folder, image_files, num_pages = pdf_to_images(rel_pdf_path, base_folder, filename)

    full_pdf_path = os.path.join(settings.MEDIA_ROOT, rel_pdf_path)
    pages_data = extract_text_boxes(full_pdf_path)
    contrasts_scores = calculate_contrast(pages_data, images_folder, filename)
    num_words_scores = calculate_num_words(pages_data)

    return {
        "pdf_path": rel_pdf_path,
        "images_folder": images_folder,
        "image_files": image_files,
        "num_pages": num_pages,
        "contrast_scores": contrasts_scores,
        "num_words_scores": num_words_scores,
    }