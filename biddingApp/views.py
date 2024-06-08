# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# Python Standard Library Imports
import math, random, requests
from datetime import date

from django.utils import timezone


# Django Imports
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView

# Project Imports
from .forms import  ApplicationForm, PaymentForm
from .models import Notice, Applicant, Application, Payment, Submission


from django.shortcuts import render, redirect, get_object_or_404
from .models import Applicant
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm




import os
import zipfile
import tempfile
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Notice
import win32com.client
import pythoncom  # Import pythoncom
from pdf2image import convert_from_path
from django.conf import settings



import os
import tempfile
import zipfile
import pythoncom
import win32com.client
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Notice
from django.conf import settings
from pdf2image import convert_from_path
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

def index(request):
    notices = Notice.objects.all().order_by('-creation_date')[:6]
    if request.user.is_authenticated and not request.user.is_superuser: 
        applicant = Applicant.objects.get(user=request.user)
        apply = Application.objects.filter(applicant=applicant)
        data = []
        for i in apply:
            data.append(i.notice.id)

        ctx = {
            'notices': notices,
            'applicant': applicant,
            'data': data
        }
        return render(request, "index.html", ctx)
    else:
        return render(request, "index.html", {'notices': notices})    
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
    
#admin index page
@login_required
def admin_home_view(request):
    notices = Notice.objects.all().order_by('-creation_date')[:6]
    return render(request, "index.html", {'notices': notices})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def user_homepage(request):
    applicant = Applicant.objects.get(user=request.user)
    if request.method == "POST":
        username = request.POST['username']  # Get the username from the form

        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']

        applicant.user.username = username  # Update the username field
        applicant.user.email = email
        applicant.phone = phone
        applicant.address = address
        applicant.user.save()
        applicant.save()

        try:
            image = request.FILES['image']
            applicant.image = image
            applicant.save()
        except:
            pass
        alert = True
        return render(request, "user/user_homepage.html", {'alert': alert})
    return render(request, "user/user_homepage.html", {'applicant': applicant})


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def all_notices(request):
    notices = Notice.objects.all().order_by('-creation_date')
    applicant = Applicant.objects.get(user=request.user)
    
    # Fetch applications for the current user
    applications = Application.objects.filter(applicant=applicant)
    application_data = [app.notice.id for app in applications]

    # Fetch submissions for the current user
    submissions = Submission.objects.filter(applicant=applicant)
    submission_data = [sub.notice.id for sub in submissions]

    return render(request, "user/all_notices.html", {'notices': notices, 'application_data': application_data, 'submission_data': submission_data})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def notice_detail(request, myid):
    notice = Notice.objects.get(id=myid)
    applicant = Applicant.objects.get(user=request.user)
    user_name = applicant.user.username
    user_mobile = applicant.phone
    user_email = applicant.user.email
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['company_name']
            email = form.cleaned_data['email']
            amount = form.cleaned_data['amount']
            phone = form.cleaned_data['phone']
            # Pass notice_id to process_payment and redirect to payment gateway
            return redirect(process_payment(name, email, amount, phone, myid))
    else:
        form = PaymentForm()
    ctx = {
        'notice': notice,
        'user_name': user_name,
        'user_mobile': user_mobile,
        'user_email': user_email,
        'form': form
    }
    return render(request, 'user/notice_detail.html', ctx)


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

def process_payment(name, email, amount, phone, notice_id):
    auth_token = 'FLWSECK_TEST-59daa1f95d2c524826c50349b6ce6d9b-X'
    hed = {'Authorization': 'Bearer ' + auth_token}
    data = {
        "tx_ref": '' + str(math.floor(1000000 + random.random() * 9000000)),
        "amount": amount,
        "currency": "UGX",
        "redirect_url": f"http://localhost:8000/callback?id={notice_id}",
        "payment_options": "card",
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": email,
            "phonenumber": phone,
            "name": name
        },
        "customizations": {
            "title": "UNOC Procurement Portal",
            "description": "Pay your Application fee",
            "logo": "https://www.unoc.co.ug/wp-content/uploads/2020/12/fevicon.png"
        }
    }
    url = 'https://api.flutterwave.com/v3/payments'
    response = requests.post(url, json=data, headers=hed)
    response_data = response.json()
    link = response_data['data']['link']
    return link

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)
    notice_id = request.GET.get('id', None)

    if status == 'successful' and tx_ref and notice_id:
        user = request.user
        Payment.objects.create(tx_ref=tx_ref, user=user, notice_id=notice_id)
        return redirect(f'/notice_apply/{notice_id}/')
    else:
        return HttpResponse('Payment was not successful.')

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
@login_required
def notice_apply(request, myid):
    applicant = Applicant.objects.get(user=request.user)
    notice = Notice.objects.get(id=myid)
    date1 = timezone.now()

    if notice.end_date < date1:
        return render(request, "user/notice_apply.html", {'closed': True})
    elif notice.start_date > date1:
        return render(request, "user/notice_apply.html", {'notopen': True})
    else:
        if request.method == "POST":
            letter = request.FILES['letter']
            Application.objects.create(notice=notice, applicant=applicant, letter=letter, apply_date=timezone.now())
            return render(request, "user/notice_apply.html", {'alert': True})
    
    return render(request, "user/notice_apply.html", {'notice': notice})


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def notice_submit(request, myid):  
    applicant = Applicant.objects.get(user=request.user)
    notice = Notice.objects.get(id=myid)
    date1 = timezone.now()

    if notice.end_date < date1:
        return render(request, "user/notice_submit.html", {'closed': True})  
    elif notice.start_date > date1:
        return render(request, "user/notice_submit.html", {'notopen': True})  
    else:
        if request.method == "POST":
            userbid = request.FILES['userbid']
            files_count = request.POST['files_attached']
            if userbid:
                # Check file extension
                file_extension = userbid.name.split('.')[-1]
                if file_extension.lower() not in ['zip', 'rar']:
                    error_message = "Invalid file format. Only zipped files are allowed."
                    return render(request, "user/notice_submit.html", {'notice': notice, 'error_message': error_message})
               
                Submission.objects.create(notice=notice, applicant=applicant, bid=userbid, submission_date=timezone.now(), files_attached=files_count)
                return render(request, "user/notice_submit.html", {'alert': True}) 
            else:
                error_message = "Please select a file."
                return render(request, "user/notice_submit.html", {'notice': notice, 'error_message': error_message})
    
    return render(request, "user/notice_submit.html", {'notice': notice})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
@login_required
def all_applicants(request):
    application = Application.objects.all()
    return render(request, "admin/all_applicants.html", {'application':application})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def all_submissions(request):
    submission = Submission.objects.all()
    return render(request, "admin/all_submissions.html", {'submission': submission})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

def signup(request):
    if request.method == "POST":
        try:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            email = request.POST['email']
            phone = request.POST['phone']
            image = request.FILES['image']

        except MultiValueDictKeyError as e:
            messages.error(request, f"Error: {e}")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        try:
            existing_user = User.objects.get(username=username)
            messages.error(request, "Username is already taken. Please choose a different one.")
            return redirect('signup')
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            applicants = Applicant.objects.create(user=user, phone=phone, image=image)
            user.save()
            applicants.save()

            login(request, user)
            return redirect('user_homepage')

        except IntegrityError as e:
            messages.error(request, f"Error: {e}")
            return redirect('signup')

    return render(request, "signup.html", {'thank': request.GET.get('thank', False)})  # Pass 'thank' as context variable

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________























from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Notice
import os
import zipfile
from pdf2image import convert_from_path
import pythoncom
import win32com.client

@login_required
def add_notice(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    if request.method == "POST":
        title = request.POST['notice_title']
        ref_no = request.POST['ref_no']
        fee = request.POST['fee']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        description = request.POST['description']
        full_notice = request.FILES.get('full_notice')
        bidding_doc = request.FILES.get('bidding_doc')

        notice = Notice.objects.create(
            title=title,
            ref_no=ref_no,
            fee=fee,
            start_date=start_date,
            end_date=end_date,
            description=description,
            full_notice=full_notice,
            bidding_doc=bidding_doc,
            creation_date=timezone.now()
        )

        # Convert full_notice to images
        notice.convert_full_notice_to_images()

        # Convert bidding_doc to images
        notice.convert_bidding_doc_to_images()

        alert = True
        return render(request, "admin/add_notice.html", {'alert': alert})
    return render(request, "admin/add_notice.html")

@login_required
def view_biddoc_images(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    zip_path = os.path.join(settings.MEDIA_ROOT, notice.preview_biddoc.name)

    # Directory to store extracted images
    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images2', str(notice_id))
    if not os.path.exists(extracted_images_dir):
        os.makedirs(extracted_images_dir)
    
    image_urls = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_images_dir)
            for filename in os.listdir(extracted_images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_urls.append(os.path.join(settings.MEDIA_URL, 'extracted_images2', str(notice_id), filename))
    except zipfile.BadZipFile:
        # Handle error if the zip file is corrupted or not a zip file
        pass

    # Log extracted image URLs for debugging
    for url in image_urls:
        print("Extracted image URL:", url)

    context = {
        'notice': notice,
        'image_urls': image_urls,
    }
    return render(request, 'user/view_biddoc_images.html', context)

@login_required
def view_full_notice_images(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    zip_path = os.path.join(settings.MEDIA_ROOT, notice.preview_notice.name)

    # Directory to store extracted images
    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images1', str(notice_id))
    if not os.path.exists(extracted_images_dir):
        os.makedirs(extracted_images_dir)
    
    image_urls = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_images_dir)
            for filename in os.listdir(extracted_images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_urls.append(os.path.join(settings.MEDIA_URL, 'extracted_images1', str(notice_id), filename))
    except zipfile.BadZipFile:
        # Handle error if the zip file is corrupted or not a zip file
        pass

    # Log extracted image URLs for debugging
    for url in image_urls:
        print("Extracted image URL:", url)

    context = {
        'notice': notice,
        'image_urls': image_urls,
    }
    return render(request, 'user/view_full_notice_images.html', context)

@login_required
def admin_view_biddoc_images(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    zip_path = os.path.join(settings.MEDIA_ROOT, notice.preview_biddoc.name)

    # Directory to store extracted images
    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images2', str(notice_id))
    if not os.path.exists(extracted_images_dir):
        os.makedirs(extracted_images_dir)
    
    image_urls = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_images_dir)
            for filename in os.listdir(extracted_images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_urls.append(os.path.join(settings.MEDIA_URL, 'extracted_images2', str(notice_id), filename))
    except zipfile.BadZipFile:
        # Handle error if the zip file is corrupted or not a zip file
        pass

    # Log extracted image URLs for debugging
    for url in image_urls:
        print("Extracted image URL:", url)

    context = {
        'notice': notice,
        'image_urls': image_urls,
    }
    return render(request, 'admin/admin_view_biddoc_images.html', context)

@login_required
def admin_view_full_notice_images(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    zip_path = os.path.join(settings.MEDIA_ROOT, notice.preview_notice.name)

    # Directory to store extracted images
    extracted_images_dir = os.path.join(settings.MEDIA_ROOT, 'extracted_images1', str(notice_id))
    if not os.path.exists(extracted_images_dir):
        os.makedirs(extracted_images_dir)
    
    image_urls = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_images_dir)
            for filename in os.listdir(extracted_images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_urls.append(os.path.join(settings.MEDIA_URL, 'extracted_images1', str(notice_id), filename))
    except zipfile.BadZipFile:
        # Handle error if the zip file is corrupted or not a zip file
        pass

    # Log extracted image URLs for debugging
    for url in image_urls:
        print("Extracted image URL:", url)

    context = {
        'notice': notice,
        'image_urls': image_urls,
    }
    return render(request, 'admin/admin_view_full_notice_images.html', context)







import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notice
import shutil

@login_required
def edit_notice(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    notice = get_object_or_404(Notice, id=myid)
    if request.method == "POST":
        title = request.POST['notice_title']
        ref_no = request.POST['ref_no']
        fee = request.POST['fee']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        description = request.POST['description']
        full_notice = request.FILES.get('full_notice')
        bidding_doc = request.FILES.get('bidding_doc')

        # Update basic fields
        notice.title = title
        notice.ref_no = ref_no
        notice.fee = fee
        notice.description = description

        # Handle full_notice update
        if full_notice:
            # Delete old full_notice files
            if notice.full_notice:
                old_full_notice_path = notice.full_notice.path
                if os.path.exists(old_full_notice_path):
                    os.remove(old_full_notice_path)
                old_preview_notice_path = os.path.splitext(old_full_notice_path)[0] + '.zip'
                if os.path.exists(old_preview_notice_path):
                    os.remove(old_preview_notice_path)
                old_images_folder = tempfile.gettempdir()
                shutil.rmtree(old_images_folder, ignore_errors=True)
            
            # Save the new full_notice
            notice.full_notice = full_notice
            notice.save()
            # Convert the new full_notice to images
            notice.convert_full_notice_to_images()

        # Handle bidding_doc update
        if bidding_doc:
            # Delete old bidding_doc files
            if notice.bidding_doc:
                old_bidding_doc_path = notice.bidding_doc.path
                if os.path.exists(old_bidding_doc_path):
                    os.remove(old_bidding_doc_path)
                old_pdf_path = os.path.splitext(old_bidding_doc_path)[0] + '.pdf'
                if os.path.exists(old_pdf_path):
                    os.remove(old_pdf_path)
                old_preview_biddoc_path = os.path.splitext(old_pdf_path)[0] + '.zip'
                if os.path.exists(old_preview_biddoc_path):
                    os.remove(old_preview_biddoc_path)
                old_images_folder = tempfile.gettempdir()
                shutil.rmtree(old_images_folder, ignore_errors=True)
            
            # Save the new bidding_doc
            notice.bidding_doc = bidding_doc
            notice.save()
            # Convert the new bidding_doc to images
            notice.convert_bidding_doc_to_images()

        # Update dates if provided
        if start_date:
            notice.start_date = start_date
        if end_date:
            notice.end_date = end_date

        notice.save()
        alert = True
        return render(request, "admin/edit_notice.html", {'alert': alert, 'notice': notice})
    return render(request, "admin/edit_notice.html", {'notice': notice})
















# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
@login_required
def notice_list(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    notices = Notice.objects.all().order_by('-creation_date')
    return render(request, "admin/notice_list.html", {'notices':notices})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________









# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
def Logout(request):
    logout(request)
    return redirect('/')

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user.is_superuser:
            login(request, user)
            return redirect("/all_applicants")
        else:
            alert = True
            return render(request, "admin/admin_login.html", {"alert":alert})
    return render(request, "admin/admin_login.html")

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def view_applicants(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    
    applicants = Applicant.objects.all()
    return render(request, "admin/view_applicants.html", {'applicants':applicants})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def edit_applicant(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    alert = False  # Initially set the alert to False
    if request.method == 'POST':
        new_rights = request.POST.get('rights')
        if new_rights == 'admin':
            applicant.user.is_superuser = True
            applicant.user.is_staff = True
        else:
            applicant.user.is_superuser = False
            applicant.user.is_staff = False
        applicant.user.save()
        alert = True  # Set the alert to True after saving changes
        messages.success(request, 'User details updated successfully.')
        return redirect('view_applicants')
    return render(request, 'admin/edit_applicant.html', {'applicant': applicant, 'alert': alert})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def delete_applicant(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicant = User.objects.filter(id=myid)
    applicant.delete()
    return redirect("/view_applicants")

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def delete_order(request):      #deletes applications
    if request.method == 'GET':
        application_id = request.GET.get('application_id')
        order = get_object_or_404(Application, application_id=application_id)
        order.delete()
        return redirect('all_applicants')
    else:
        return redirect('all_applicants')  # Handle non-GET requests as needed
    
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
    
@login_required
def user_applicants(request):
    application = Application.objects.all()
    return render(request, "admin/all_applicants.html", {'application':application})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required 
def user_applications(request):
    # Retrieve the applications of the currently logged-in user
    user_application = Application.objects.filter(applicant__user=request.user)

    return render(request, "user/user_applications.html", {'user_application': user_application})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def user_submissions(request):
    user_submission = Submission.objects.filter(applicant__user=request.user)
    return render(request, "user/user_submissions.html", {'user_submission': user_submission})


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

class NoticeDeleteView(DeleteView):
    model = Notice
    success_url = reverse_lazy('notice_list')  # Redirect after deletion


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
@login_required
def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'admin/payment_list.html', {'payments': payments})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def delete_payment(request, payment_id):
    if request.method == 'POST':
        payment = Payment.objects.get(pk=payment_id)
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
    return redirect('payment_list')

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def user_payment_list(request):
    user_payments = Payment.objects.filter(user=request.user)
    return render(request, 'user/user_payment_list.html', {'user_payments': user_payments})

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________



@login_required
def add_application(request):
    # Fetch notice and applicant data
    notices = Notice.objects.all()
    applicants = Applicant.objects.all()
    alert = False  # Initialize alert variable

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data and set the apply_date field
            application = form.save(commit=False)
            application.apply_date = timezone.now()  # Set the apply_date to the current date/time
            application.save()
            alert = True  # Set alert to True
            return redirect('all_applicants')  # Redirect to a success URL
    else:
        form = ApplicationForm()
    return render(request, 'admin/add_application.html', {'form': form, 'notices': notices, 'applicants': applicants, 'alert': alert})


# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def delete_order3(request):      #deletes submissions
    if request.method == 'GET':
        submission_id = request.GET.get('submission_id')
        order3 = get_object_or_404(Submission, submission_id=submission_id)
        order3.delete()
        return redirect('all_submissions')
    else:
        return redirect('all_submissions')  # Handle non-GET requests as needed
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def chat(request):
    admins = User.objects.filter(is_staff=True)
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('chat')
        
    else:
        form = MessageForm()
    context = {'admins': admins, 'form': form}
    return render(request, 'chat.html', context)

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@login_required
def admin_messages(request):
    received_messages = request.user.received_messages.all()
    context = {'received_messages': received_messages}
    return render(request, 'admin_messages.html', context)

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


@login_required
def delete_message(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
        if message.receiver == request.user:
            message.delete()
            messages.success(request, 'Message deleted successfully.')
        else:
            messages.error(request, 'You are not authorized to delete this message.')
    except Message.DoesNotExist:
        messages.error(request, 'Message does not exist.')
    return redirect('admin_messages')

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

#FORM 11 

def form11_view(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")    
    notice = get_object_or_404(Notice, id=myid)
    submissions = Submission.objects.filter(notice=notice).order_by('submission_date')
    notice_ref = notice.ref_no.split('/')

    context={
        'notice': notice,
        'submissions': submissions,
        'notice_ref': notice_ref
    }
    return render(request, "admin/form11.html", context)
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


def get_applicant_emails(request):
    notices = Notice.objects.all()  # Fetch all notices
    selected_notice_id = request.GET.get('notice_id')
    selected_type = request.GET.get('type')
    
    items = []
    if selected_notice_id and selected_type:
        if selected_type == 'application':
            applications = Application.objects.filter(notice_id=selected_notice_id)
            items = [(application.applicant.user.username, application.applicant.user.email) for application in applications]
        elif selected_type == 'submission':
            submissions = Submission.objects.filter(notice_id=selected_notice_id)
            items = [(submission.applicant.user.username, submission.applicant.user.email) for submission in submissions]

    return render(request, 'admin/applicant_emails.html', {
        'notices': notices,
        'items': items,
        'selected_notice_id': int(selected_notice_id) if selected_notice_id else None,
        'selected_type': selected_type,
    })

# __________________________________________________________________________________________________________________________________________________________








