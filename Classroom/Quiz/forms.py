from django import forms

class EssaySubmissionForm(forms.Form):
    images = forms.FileField(
        widget=forms.FileInput(attrs={
            'multiple': True,
            'accept': 'image/*'
        }),
        label="Upload essay images",
        help_text="Select multiple images of your handwritten essay"
    )