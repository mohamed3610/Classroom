# from django.db import models
# from django.contrib.auth import get_user_model

# class WritingQuiz(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     criteria = models.TextField()

#     def __str__(self):
#         return self.title


# class WritingSubmission(models.Model):
#     student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     quiz = models.ForeignKey('WritingQuiz', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='submissions/', null=True, blank=True)
#     extracted_text = models.TextField(null=True, blank=True)
#     feedback = models.TextField()
#     grade = models.FloatField(null = True , blank = True)
#     submission_date = models.DateField(auto_now_add = True)
#     is_graded = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.student.username} - {self.quiz.title}"
    
#     # Extend the User model with a StudentProfile
# class StudentProfile(models.Model):
#     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
#     approved = models.BooleanField(default=False)  # Track approval status
#     # Any other student-specific fields can go here, like profile picture, etc.

#     def __str__(self):
#         return self.user.username


# # Model to store course materials
# class CourseMaterial(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()  # You can also use FileField for uploaded files
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title


