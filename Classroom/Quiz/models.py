from django.db import models
from Users.models import Student , Class
from django.utils import timezone


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Class , on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    def is_active(self):
        if self.due_date:
            return timezone.now() < self.due_date
        return True  # No due date means always active

    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    image = models.ImageField(upload_to='submissions/')
    extracted_text = models.TextField(blank=True, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}"