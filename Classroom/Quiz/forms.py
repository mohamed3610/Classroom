from django import forms
from django.forms import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is not None:
            self.attrs.update(attrs)
        else:
            self.attrs = {}
        self.attrs['multiple'] = True  # Allow multiple file selection

class EssaySubmissionForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
        label="Upload images of your essay",
        help_text="Select multiple images of your handwritten essay pages."
    )

    def clean_images(self):
        """
        Custom validation for the uploaded images.
        """
        images = self.files.getlist('images')  # Get all uploaded files
        if not images:
            raise forms.ValidationError("Please upload at least one image.")

        for image in images:
            # Validate file size (e.g., 5MB limit)
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(f"File {image.name} is too large. Maximum size is 5MB.")

            # Validate file type (e.g., only images)
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError(f"File {image.name} is not a valid image.")

        return images