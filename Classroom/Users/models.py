from django.db import models

from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('superuser', 'SuperUser'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    device_count = models.PositiveIntegerField(default=0)  # For tracking student device usage

    def __str__(self):
        return self.username

    # Check if the user is a student and device limit is reached
    def can_login_from_device(self):
        if self.user_type == 'student' and self.device_count >= 2:
            return False
        return True


class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255, unique=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_id}"
    

