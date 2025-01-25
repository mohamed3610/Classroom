from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
class Class(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_ta = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return self.username


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    guardian_name = models.CharField(max_length=40)
    guardian_relationship = models.CharField(max_length=50)
    guardian_email = models.EmailField()
    guardian_phone_number = models.CharField(max_length=15)
    guardian_whatsapp_number = models.CharField(max_length=15)
    guardian_alternate_number = models.CharField(max_length=15, blank=True, null=True)
    student_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    bank_statement = models.FileField(upload_to='bank_statements/', null=True, blank=True)
    is_bank_statement_submitted = models.BooleanField(default=False)
    is_enrolled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    


class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='devices')
    user_agent = models.CharField(max_length=255)  # Browser user agent
    cookie = models.CharField(max_length=255)  # Unique cookie for the device
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_agent}"
    







