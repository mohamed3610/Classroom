from django.shortcuts import render
import uuid
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Device, CustomUser

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import Student, CustomUser

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