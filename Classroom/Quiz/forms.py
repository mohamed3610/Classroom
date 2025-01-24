from django import forms

class EssaySubmissionForm(forms.Form):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label="Upload images of your essay"
    )