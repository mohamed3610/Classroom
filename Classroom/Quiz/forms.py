from django import forms

class EssaySubmissionForm(forms.Form):
    pdf_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
        label="Upload your essay PDF",
        help_text="Select a PDF file of your essay (max 5MB)."
    )

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if not pdf_file:
            raise forms.ValidationError("Please upload a PDF file.")
        
        # Validate file size (5MB limit)
        if pdf_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File is too large. Maximum size is 5MB.")
        
        # Validate file type
        if pdf_file.content_type != 'application/pdf':
            raise forms.ValidationError("Invalid file type. Only PDFs are accepted.")
        
        return pdf_file