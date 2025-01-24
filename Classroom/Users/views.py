from django.shortcuts import render
import uuid
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Device, CustomUser

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import Student, CustomUser
from django.core.files.storage import default_storage

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)
            user.is_student = True
            user.save()

            # Save the guardian details to the Student model
            student = Student.objects.create(
                user=user,
                guardian_name=form.cleaned_data['guardian_name'],
                guardian_relationship=form.cleaned_data['guardian_relationship'],
                guardian_email=form.cleaned_data['guardian_email'],
                guardian_phone_number=form.cleaned_data['guardian_phone_number'],
                guardian_whatsapp_number=form.cleaned_data['guardian_whatsapp_number'],
                guardian_alternate_number=form.cleaned_data['guardian_alternate_number'],
                bank_statement=form.cleaned_data['bank_statement']
            )

            # Send emails based on whether the bank statement was uploaded
            if student.bank_statement:
                # Bank statement uploaded
                send_email(
                    subject="Application Under Review",
                    template_name="emails/application_under_review.html",
                    context={"student": student},
                    recipient_list=[user.email, student.guardian_email]
                )
            else:
                # Bank statement not uploaded
                send_email(
                    subject="Bank Statement Required",
                    template_name="emails/bank_statement_required.html",
                    context={"student": student},
                    recipient_list=[user.email, student.guardian_email]
                )

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def send_email(subject, template_name, context, recipient_list):
    """
    Helper function to send emails.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

def application_under_review(request):
    return render(request, 'application_under_review.html')


def handle_upload(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to upload a bank statement.')
        return redirect('login')  # Redirect to login page if the user is not authenticated

    try:
        student = request.user.student_profile  # Get the student profile of the logged-in user
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')  # Redirect to home or another page if the student profile doesn't exist

    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.FILES.get('bank_statement')  # Get the uploaded file
        if uploaded_file:
            # Save the file to the student's bank_statement field
            student.bank_statement = uploaded_file
            student.save()

            # Show a success message
            messages.success(request, 'Bank statement uploaded successfully!')
            return redirect('application_under_review')  # Redirect to the same page after upload
        else:
            # Show an error message if no file is uploaded
            messages.error(request, 'No file was uploaded. Please try again.')
            return redirect('upload_bank_statement')

    # Render the upload form for GET requests
    return render(request, 'second-page.html')


def device_limit_reached(request):
    return render(request, 'device_limit_reached.html')