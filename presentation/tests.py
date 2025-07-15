from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .utils import contrast_to_stars, luminance, extract_text_boxes
import fitz
import os
import shutil
from .models import Presentation

class PresentationViewsTests(TestCase):

    def setUp(self):
        pass

# This is a system test
class UtilsSavePDFTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test_User', password='secret')
        self.client = Client()
        self.client.login(username='Test_User', password='secret')
        self.test_pdf_location = 'test_pdf/single_page.pdf'
        self.test_pdf_for_image_test_case = 'test_pdf/multiple_page.pdf'
        self.invalid_pdf_location = 'test_pdf/image_as_pdf.pdf'
        self.zero_sized_pdf_location = 'test_pdf/empty_file.pdf'
        self.too_large_pdf_location = 'test_pdf/too_large.pdf'
        self.some_other_file_location = 'test_pdf/something_else.doc'
        self.filename = "Test Example"
        self.upload_folder = os.path.join('media', 'uploads', 'Test_User')

        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)

    def test_pdf_upload_successful(self):
        ''' Normal PDF file is uploaded '''
        with open(self.test_pdf_location, 'rb') as pdf_file:
            _ = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        saved_path = os.path.join(
            'media', 'uploads', 'Test_User', self.filename, self.filename + '.pdf'
        )
        self.assertTrue(os.path.exists(saved_path)) # This means the PDF was saved there

    def test_images_obtained_from_successful_pdf_upload(self):
        ''' Images folder test '''
        with open(self.test_pdf_for_image_test_case, 'rb') as pdf_file:
            _ = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        saved_path = os.path.join(
            'media', 'uploads', 'Test_User', self.filename
        )
        self.assertTrue(os.path.exists(saved_path)) # The images folder is created
        _, _, files = next(os.walk(saved_path + "/images"))
        file_count = len(files)
        self.assertEqual(file_count, 7)

        for item in range(0, len(files)):
            self.assertEqual(files[item].split(".")[1], "png") # Testing the extension

    def test_invalid_pdf_upload_attempt(self):
        ''' In this case, an image, pretending being a PDF file, is uploaded '''
        with open(self.invalid_pdf_location, 'rb') as pdf_file:
            response = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        self.assertEqual(response.status_code, 200)  # It stays on the same page
        self.assertFormError(response, 'form', 'pdf_file', "The uploaded file is not a valid PDF.")

        # No file is saved
        self.assertFalse(Presentation.objects.filter(title=self.filename).exists())

    def test_zero_size_pdf_upload_attempt(self):
        ''' In this case, a 0 size PDF file is uploaded '''
        with open(self.zero_sized_pdf_location, 'rb') as pdf_file:
            response = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        self.assertEqual(response.status_code, 200)  # It stays on the same page
        self.assertFormError(response, 'form', 'pdf_file', "The submitted file is empty.")

        # No file is saved
        self.assertFalse(Presentation.objects.filter(title=self.filename).exists())

    def test_too_large_pdf_upload_attempt(self):
        ''' In this case, a 5.5 MB PDF file is uploaded. Limit is 5 MB '''
        with open(self.too_large_pdf_location, 'rb') as pdf_file:
            response = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        self.assertEqual(response.status_code, 200)  # It stays on the same page
        self.assertFormError(response, 'form', 'pdf_file', "The file is too large (max 5 MB).")

        # No file is saved
        self.assertFalse(Presentation.objects.filter(title=self.filename).exists())

    def test_other_file_upload_attempt(self):
        ''' In this case, a 5.5 MB PDF file is uploaded. Limit is 5 MB '''
        with open(self.some_other_file_location, 'rb') as pdf_file:
            response = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
        
        self.assertEqual(response.status_code, 200)  # It stays on the same page
        self.assertFormError(response, 'form', 'pdf_file', "Only PDF files are allowed.")

        # No file is saved
        self.assertFalse(Presentation.objects.filter(title=self.filename).exists())

    def tearDown(self):
        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)

class UtilsExtractTextBoxes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test_User', password='secret')
        self.client = Client()
        self.client.login(username='Test_User', password='secret')
        self.test_pdf_location = 'test_pdf/single_page.pdf'
        self.upload_folder = os.path.join('media', 'uploads', 'Test_User')
        self.filename = "Test Text Extraction"

        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)

    def test_pdf_extract_words(self):
        ''' Word extraction is performed here '''
        with open(self.test_pdf_location, 'rb') as pdf_file:
            _ = self.client.post(
                reverse('presentation:upload'), 
                {'title': self.filename,
                'pdf_file': pdf_file}
            )
    
        saved_path = os.path.join(
            'media', 'uploads', 'Test_User', self.filename, self.filename + '.pdf'
        )

        # This document has exactly one page
        text_boxes = extract_text_boxes(saved_path)
        self.assertEqual(len(text_boxes), 1) # Testing for 1 page
        self.assertEqual(text_boxes[0]["page"], 1) # Testing if the data is consistent

        self.assertEqual(text_boxes[0]["text_boxes"][0]["text"], "07/15/2025") # First text found
        self.assertEqual(text_boxes[0]["text_boxes"][1]["text"], "Contrast test case") # Second text found
    
    def tearDown(self):
        if os.path.exists(self.upload_folder):
            shutil.rmtree(self.upload_folder)

class UtilsPdfToImgTest(TestCase):
    def setUp(self):
        self.single_page_file = "/test_pdf/single_page.pdf"
        self.multiple_page_file = "/test_pdf/multiple_page.pdf"

    def test_pdf_image_single_page_pdf(self):
        """Calculate the score on the Contrast.pdf test pdf"""
        pass

    def test_pdf_image_multiple_page_pdf(self):
        """Calculate the score on the Contrast.pdf test pdf"""
        pass

class UtilsContrastTests(TestCase):
    def setUp(self):
        self.bg_white = (255,255,255)

    def test_black_text_white_bg(self):
        """ Calculate the contrast score between a black text against a white background """
        text = (0,0,0)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg) + 0.05) / (min(lum_text, lum_bg) + 0.05)
        self.assertEqual(contrast_ratio, 21)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 5)

    def test_high_text_contrast(self):
        """ Contrast that yield 5 stars, this mean its over 12 """
        text = (134,0,45)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg) + 0.05) / (min(lum_text, lum_bg) + 0.05)
        self.assertGreater(contrast_ratio, 10)
        self.assertLess(contrast_ratio, 11)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 5)

    def test_good_text_contrast(self):
        """ Contrast that yield 4 stars, this mean its between 8 and 10 """
        text = (21,89,92)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg) + 0.05) / (min(lum_text, lum_bg) + 0.05)
        self.assertGreater(contrast_ratio, 8)
        self.assertLess(contrast_ratio, 9)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 4)

    def test_moderate_text_contrast(self):
        """ Contrast that yield 3 stars, this mean its between 5 and 8 """
        text = (63,124,30)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg) + 0.05) / (min(lum_text, lum_bg) + 0.05)
        self.assertGreater(contrast_ratio, 5)
        self.assertLess(contrast_ratio, 6)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 3)

    def test_low_contrast(self):
        """ Contrast that yield 2 stars, this mean its between 3 and 5 """
        text = (168,135,111)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg)+0.05) / (min(lum_text, lum_bg)+0.05)
        self.assertGreater(contrast_ratio, 3)
        self.assertLess(contrast_ratio, 4)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 2)
    
    def test_lowest_contrast(self):
        """ Contrast that yield 1 star, this mean its less than 3"""
        text = (219,238,255)
        lum_text = luminance(text)
        lum_bg = luminance(self.bg_white)
        contrast_ratio = (max(lum_text, lum_bg)+0.05) / (min(lum_text, lum_bg)+0.05)
        self.assertLess(contrast_ratio, 2)
        stars = contrast_to_stars(contrast_ratio)
        self.assertEqual(stars, 1)



class UtilsLuminanceTests(TestCase):

    def test_black(self):
        self.assertAlmostEqual(luminance((0,0,0)), 0.0, places=5)

    def test_white(self):
        self.assertAlmostEqual(luminance((255,255,255)), 1.0, places=5)

    def test_mid_gray(self):
        lum = luminance((127,127,127)) # Gray color
        self.assertAlmostEqual(lum, 0.2159, places=2)

    def test_red(self):
        lum = luminance((255,0,0))
        expected = 0.2126
        self.assertAlmostEqual(lum, expected, places=4)

    def test_green(self):
        lum = luminance((0,255,0))
        expected = 0.7152
        self.assertAlmostEqual(lum, expected, places=4)

    def test_blue(self):
        lum = luminance((0,0,255))
        expected = 0.0722
        self.assertAlmostEqual(lum, expected, places=4)