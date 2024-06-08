import os
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.conf import settings



# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    image = models.ImageField(upload_to="logos")
    address = models.CharField(max_length=100, blank=True, null=True)

    
    def __str__(self):
        return self.user.username

    def is_admin(self):
        return self.user.is_superuser and self.user.is_staff

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

from django.db import models
from django.utils import timezone
import os
import tempfile
import zipfile
from pdf2image import convert_from_path

# class Notice(models.Model):
#     start_date = models.DateTimeField(default=timezone.now)
#     end_date = models.DateTimeField(default=timezone.now)
#     title = models.CharField(max_length=200)
#     fee = models.FloatField()
#     description = models.TextField(max_length=10000)
#     creation_date = models.DateTimeField(default=timezone.now)
#     ref_no = models.CharField(max_length=200, blank=True, null=True)
#     full_notice = models.FileField(upload_to="adverts", blank=True, null=True)
#     preview_notice = models.FileField(upload_to="preview_zips1", blank=True, null=True)

#     bidding_doc = models.FileField(upload_to="outgoing_bids", blank=True, null=True)
#     preview_biddoc = models.FileField(upload_to="preview_zips", blank=True, null=True)

#     def __str__(self):
#         return self.title

#     def convert_to_images(self):
#         if self.full_notice:
#             pdf_path = self.full_notice.path
#             images_folder = tempfile.mkdtemp()

#             # Convert PDF to images
#             pages = convert_from_path(pdf_path, 200)  # 200 DPI
#             image_paths = []
#             for i, page in enumerate(pages):
#                 image_path = os.path.join(images_folder, f'page_{i+1}.jpg')
#                 page.save(image_path, 'JPEG')
#                 image_paths.append(image_path)

#             # Zip images
#             zip_path = os.path.splitext(pdf_path)[0] + '.zip'
#             with zipfile.ZipFile(zip_path, 'w') as myzip:
#                 for image_path in image_paths:
#                     myzip.write(image_path, os.path.basename(image_path))

#             self.preview_notice = os.path.relpath(zip_path, settings.MEDIA_ROOT)
#             self.save()




import os
import tempfile
import zipfile
from django.db import models
from django.utils import timezone
from django.conf import settings
from pdf2image import convert_from_path
import pythoncom
import win32com.client

class Notice(models.Model):
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)
    fee = models.FloatField()
    description = models.TextField(max_length=10000)
    creation_date = models.DateTimeField(default=timezone.now)
    ref_no = models.CharField(max_length=200, blank=True, null=True)
    full_notice = models.FileField(upload_to="adverts", blank=True, null=True)
    preview_notice = models.FileField(upload_to="preview_zips1", blank=True, null=True)
    bidding_doc = models.FileField(upload_to="outgoing_bids", blank=True, null=True)
    preview_biddoc = models.FileField(upload_to="preview_zips", blank=True, null=True)

    def __str__(self):
        return self.title

    def convert_full_notice_to_images(self):
        if self.full_notice:
            pdf_path = self.full_notice.path
            images_folder = tempfile.mkdtemp(prefix='extracted_images1_')

            # Convert PDF to images
            pages = convert_from_path(pdf_path, 200)  # 200 DPI
            image_paths = []
            for i, page in enumerate(pages):
                image_path = os.path.join(images_folder, f'page_{i+1}.jpg')
                page.save(image_path, 'JPEG')
                image_paths.append(image_path)

            # Zip images
            zip_path = os.path.splitext(pdf_path)[0] + '.zip'
            with zipfile.ZipFile(zip_path, 'w') as myzip:
                for image_path in image_paths:
                    myzip.write(image_path, os.path.basename(image_path))

            self.preview_notice = os.path.relpath(zip_path, settings.MEDIA_ROOT)
            self.save()

    def convert_bidding_doc_to_images(self):
        if self.bidding_doc:
            doc_path = self.bidding_doc.path
            pdf_path = os.path.splitext(doc_path)[0] + '.pdf'
            images_folder = tempfile.mkdtemp(prefix='extracted_images2_')

            pythoncom.CoInitialize()  # Initialize COM library
            try:
                # Convert DOCX to PDF
                Application = win32com.client.Dispatch("Word.Application")
                doc = Application.Documents.Open(doc_path)
                doc.ExportAsFixedFormat(pdf_path, 17)  # 17 stands for PDF format
                doc.Close()
                Application.Quit()

                # Convert PDF to images
                pages = convert_from_path(pdf_path, 200)  # 200 DPI
                image_paths = []
                for i, page in enumerate(pages):
                    image_path = os.path.join(images_folder, f'page_{i+1}.jpg')
                    page.save(image_path, 'JPEG')
                    image_paths.append(image_path)

                # Zip images
                zip_path = os.path.splitext(pdf_path)[0] + '.zip'
                with zipfile.ZipFile(zip_path, 'w') as myzip:
                    for image_path in image_paths:
                        myzip.write(image_path, os.path.basename(image_path))

                self.preview_biddoc = os.path.relpath(zip_path, settings.MEDIA_ROOT)
                self.save()
            finally:
                pythoncom.CoUninitialize()  # Uninitialize COM library


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
class Application(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    letter = models.FileField(upload_to="letters")
    apply_date = models.DateTimeField(default=timezone.now)  
    bid_document = models.FileField(upload_to="", blank=True, null=True)
    application_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True
    )


    def __str__ (self):
        return str(self.applicant)

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
class Payment(models.Model):
    tx_ref = models.CharField(max_length=255, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"Payment for Notice: {self.notice_id} by User: {self.user_id}"
    
# _________________________________________________________________________________________________________________________________________________________________________________________________________________________________
class Submission(models.Model): 
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    bid = models.FileField(upload_to="bids", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['zip','rar'])])  #letter
    submission_date = models.DateTimeField(default=timezone.now) #apply_date   
    files_attached = models.CharField(max_length=10, blank=True, null=True)
    submission_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True
    )

    def __str__ (self):
        return str(self.applicant)
    
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.CharField(max_length=200,blank=True)
    file = models.FileField(upload_to='message_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content}"

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
