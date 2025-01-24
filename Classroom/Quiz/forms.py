from django import forms

from django.forms import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is not None:
            self.attrs.update(attrs)
        else:
            self.attrs = {}
        self.attrs['multiple'] = True

class EssaySubmissionForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
        label="Upload images of your essay"
    )