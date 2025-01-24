from django.urls import path
from . import views

urlpatterns = [
    # path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    # path('quiz/result/<int:submission_id>/', views.quiz_result, name='quiz_result'),
    # path('course-material/', views.course_material, name='course_material'),
    # path('grades/', views.grades, name='grades'),
    #  path('essay/<int:quiz_id>/', views.essay_detail, name='essay_detail'),
    path('' , views.index , name="landing_page"),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_result/<int:submission_id>/', views.quiz_result, name='quiz_result'),
    

]
