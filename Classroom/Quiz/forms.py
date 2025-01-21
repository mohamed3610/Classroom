from django import forms
from .models import WritingQuiz, WritingSubmission

class WritingQuizForm(forms.ModelForm):
    class Meta:
        model = WritingSubmission
        fields = ['image']

class WritingQuizCreateForm(forms.ModelForm):
    class Meta:
        model = WritingQuiz
        fields = ['title', 'description', 'criteria']
