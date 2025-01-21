from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view , application_under_review
urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/signup/', signup_view, name='signup'),
    path('application-under-review/', application_under_review, name='application_under_review'),

    
]