from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('student-cms/', views.student_cms, name='student_cms'),
    path('grades/', views.grades_page, name='grades_page'),
    path('quizzes/', views.quizzes_page, name='quizzes_page'),
]