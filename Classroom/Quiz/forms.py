from django import forms

class EssaySubmissionForm(forms.Form):
    images = forms.FileField(
        widget=forms.FileInput(attrs={
            'multiple': True,
            'accept': 'image/*'  # Optional: restrict to image files
        }),
        label="Upload images of your essay",
        help_text="Select multiple images of your handwritten essay"
    )