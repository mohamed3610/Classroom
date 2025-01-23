from django.urls import path
from . import views

urlpatterns = [
    # Other URLs
    path('student-cms/', views.student_cms, name='student_cms'),
]