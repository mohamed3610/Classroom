from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view , application_under_review , handle_upload
urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/signup/', signup_view, name='signup'),
    path('application-under-review/', application_under_review, name='application_under_review'),
    path('upload/', handle_upload, name='handle_upload'),
    path('device-limit-reached/', device_limit_reached, name='device-limit-reached'),

    
]