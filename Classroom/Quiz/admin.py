from django.contrib import admin
from .models import Quiz, Submission
import http.client
import json

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_at', 'due_date', 'is_published', 'is_active')
    list_filter = ('group', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructions')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Is Active'

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'submitted_at', 'grade', 'is_graded', 'is_confirmed')
    list_filter = ('quiz', 'is_graded', 'is_confirmed', 'submitted_at')
    search_fields = ('student__user__username', 'quiz__title', 'extracted_text')
    date_hierarchy = 'submitted_at'
    ordering = ('submitted_at',)
    readonly_fields = ('submitted_at',)

    # Custom actions
    actions = ['mark_as_graded', 'confirm_submission_and_notify']

    def mark_as_graded(self, request, queryset):
        queryset.update(is_graded=True)
    mark_as_graded.short_description = "Mark selected submissions as graded"

    def confirm_submission_and_notify(self, request, queryset):
        for submission in queryset:
            # Mark the submission as confirmed
            submission.is_confirmed = True
            submission.save()

            # Send WhatsApp notification to the guardian
            self.send_whatsapp_notification(submission)

        self.message_user(request, f"{queryset.count()} submissions confirmed and guardians notified.")
    confirm_submission_and_notify.short_description = "Confirm submissions and notify guardians"

    def send_whatsapp_notification(self, submission):
        """
        Sends a WhatsApp text message to the guardian with the quiz title, grade, and feedback.
        """
        guardian_whatsapp_number = submission.student.guardian_whatsapp_number
        message = (
            f"Dear {submission.student.guardian_name},\n\n"
            f"Your ward, {submission.student.user.username}, has received the following result:\n\n"
            f"*Quiz Title*: {submission.quiz.title}\n"
            f"*Grade*: {submission.grade}%\n"
            f"*Feedback*: {submission.feedback}\n\n"
            f"Best regards,\nShaymaa's English Classes"
        )

        # Prepare the payload for the WhatsApp API
        payload = {
            "number": guardian_whatsapp_number,  
            "message": message
        }

        # Convert payload to JSON
        payload_json = json.dumps(payload)

        # Set up the API connection
        conn = http.client.HTTPSConnection("whatsapp-api5.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c",  # Replace with your RapidAPI key
            'x-rapidapi-host': "whatsapp-api5.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        try:
            # Make the API request
            conn.request("POST", "/api/v2/send_text/", payload_json, headers)
            res = conn.getresponse()
            data = res.read()

            # Log the response
            print(f"WhatsApp API Response: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Failed to send WhatsApp message: {e}")
        finally:
            conn.close()