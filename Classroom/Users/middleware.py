# your_app/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import Device
from django.urls import reverse
import uuid

class DeviceTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get the user's IP address

            # Get the user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Get or create a unique cookie for the device
            device_cookie = request.COOKIES.get('device_id')
            if not device_cookie:
                device_cookie = str(uuid.uuid4())  # Generate a unique ID for the device

            # Check if the device is already registered
            user_devices = Device.objects.filter(user=request.user)

            if not user_devices.filter(cookie=device_cookie).exists():
                if user_devices.count() >= 3:
                    # Log the user out if they exceed the device limit
                    logout(request)
                    return redirect('device-limit-reached')

                # Register the new device
                Device.objects.create(
                    user=request.user,
                    user_agent=user_agent,
                    cookie=device_cookie,
                )

            # Set the device cookie in the response
            request.device_cookie = device_cookie

    def process_response(self, request, response):
        if hasattr(request, 'device_cookie'):
            response.set_cookie('device_id', request.device_cookie, max_age=365*24*60*60)  # 1 year
        return response

class EnrollmentCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Precompute reverse lookups for excluded paths
        self.excluded_paths = [
            reverse('application_under_review'),
            reverse('handle_upload'),
            reverse('landing_page')
        ]

    def __call__(self, request):

        # Exclude specific pages from the middleware check
        if request.path.rstrip('/') in [path.rstrip('/') for path in self.excluded_paths]:
            return self.get_response(request)

        # Check if the user is authenticated and is a student
        student = getattr(request.user, 'student_profile', None)
        if request.user.is_authenticated and student:
            # Redirect unenrolled students to the "under review" page
            if not student.is_enrolled:
                return redirect('application_under_review')
            else:
                return redirect('cms:student_cms')

        # Proceed with the request
        return self.get_response(request)