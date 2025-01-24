from django.contrib import admin
from .models import Quiz, Submission
import requests
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
        Sends a WhatsApp message to the guardian using the WhatsApp API.
        """
        guardian_whatsapp_number = submission.student.guardian_whatsapp_number
        message = (
            f"Dear {submission.student.guardian_name},\n\n"
            f"Your ward, {submission.student.user.username}, has received a grade of {submission.grade}% "
            f"for the quiz '{submission.quiz.title}'. Please check the platform for more details.\n\n"
            f"Best regards,\nShaymaa's English Classes"
        )

        url = "https://whatsapp-messaging-hub.p.rapidapi.com/WhatsappSendMessage"
        payload = {
            "token": "K0SBmydcX4ASHUM54sT1HuO6L1OAW+j+xcLrN+VZ2hFPV/SHnkTOpYVODr6VNMBbm7qsSrSrMduuL0PGZKxHow==",  # Replace with your actual token
            "phone_number_or_group_id": guardian_whatsapp_number,
            "is_group": False,
            "message": message,
            "quoted_message_id": "",
            "quoted_phone_number": "",
            "reply_privately": False,
            "reply_privately_group_id": ""
        }
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c",  # Replace with your actual API key
            "X-RapidAPI-Host": "whatsapp-messaging-hub.p.rapidapi.com"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"WhatsApp message sent to {guardian_whatsapp_number}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send WhatsApp message: {e}")