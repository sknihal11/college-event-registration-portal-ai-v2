from django import forms
from .models import UserProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'college_email',
            'registration_number',
            'branch',
            'department',
            'year_of_study',
        ]
        widgets = {
            'college_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter college email'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration number'
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department'
            }),
            'year_of_study': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields mandatory in the form
        self.fields['college_email'].required = True
        self.fields['registration_number'].required = True
        self.fields['branch'].required = True
        self.fields['department'].required = True
        self.fields['year_of_study'].required = True

    def clean_college_email(self):
        email = self.cleaned_data['college_email'].strip().lower()

        # Allow only college email domain (change if needed)
        allowed_domain = "mvgrce.edu.in"
        if not email.endswith(f"@{allowed_domain}"):
            raise forms.ValidationError(f"Please use your college email (@{allowed_domain}).")

        return email

    def clean_registration_number(self):
        reg_no = self.cleaned_data['registration_number'].strip()

        # Optional normalization
        return reg_no