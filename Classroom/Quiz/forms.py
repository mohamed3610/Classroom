from django import forms

class EssaySubmissionForm(forms.Form):
    images = forms.MultipleFileField(
        widget=forms.FileInput(attrs={
            'multiple': True,
            'class': 'file-input',
            'accept': 'image/*'
        }),
        label="Upload Essay Images",
        help_text="Select multiple images of your handwritten essay pages"
    )