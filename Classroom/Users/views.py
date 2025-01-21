from django.shortcuts import render
import uuid
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Device, CustomUser

def login_view(request):
    # Your logic to authenticate the user
    user = authenticate(username=request.POST['username'], password=request.POST['password'])

    if user is not None:
        if user.can_login_from_device():
            login(request, user)

            # Generate a device ID if not already in the cookies
            device_id = request.COOKIES.get('device_id')
            if not device_id:
                # Generate a new device ID and set it in the user's cookies
                device_id = str(uuid.uuid4())
                response = HttpResponse("Device registered")
                response.set_cookie('device_id', device_id, max_age=60*60*24*365)  # 1 year expiry
            else:
                response = HttpResponse("Device recognized")
            
            # Check if the device is new for this user
            if not Device.objects.filter(user=user, device_id=device_id).exists():
                # It's a new device, so add it to the database
                if user.user_type == 'student':
                    if user.device_count < 2:
                        Device.objects.create(user=user, device_id=device_id)
                        user.device_count += 1
                        user.save()
                    else:
                        return redirect('device_limit_reached')  # Device limit reached
            return response  # Redirect or send response as needed
        else:
            # Handle case where device limit is reached
            return redirect('device_limit_reached')
    else:
        # Authentication failed
        return redirect('login_failed')
