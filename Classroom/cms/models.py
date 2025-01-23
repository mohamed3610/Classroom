from django.db import models
from Users.models import Class
class CourseMaterial(models.Model):
    group = models.ForeignKey(Class , on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='course_materials/')
    description = models.TextField()

    def __str__(self):
        return self.title
    


class Grades(models.Model):
    student = models.ForeignKey('Users.Student', on_delete=models.CASCADE, related_name='student_grades')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject}: {self.score}"