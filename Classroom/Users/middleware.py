# your_app/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Device
from .utils import generate_device_hash
from django.urls import reverse

class DeviceTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.is_student:
            device_hash = generate_device_hash(request)
            user_devices = Device.objects.filter(user=request.user)

            if not user_devices.filter(device_id=device_hash).exists():
                if user_devices.count() >= 3:
                    # Log the user out if they exceed the device limit
                    logout(request)
                    return redirect('device-limit-reached')

                # Register the new device
                Device.objects.create(user=request.user, device_id=device_hash)



class EnrollmentCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Precompute reverse lookups for excluded paths
        self.excluded_paths = [
            reverse('application_under_review'),
            reverse('handle_upload'),
        ]

    def __call__(self, request):
        logger.info(f"Middleware invoked for path: {request.path}")

        # Exclude specific pages from the middleware check
        if request.path.rstrip('/') in [path.rstrip('/') for path in self.excluded_paths]:
            return self.get_response(request)

        # Check if the user is authenticated and is a student
        student = getattr(request.user, 'student_profile', None)
        if request.user.is_authenticated and student:
            # Redirect unenrolled students to the "under review" page
            if not student.is_enrolled:
                return redirect('application_under_review')

        # Proceed with the request
        return self.get_response(request)