# career_edge/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Job, JobApplication, UserProfile, JobProvider

from django import forms
from .models import Job# forms.py
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'location', 'skills', 'salary', 'job_type', 'experience_level']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Job Description', 'required': True}),
            'company': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Company Website URL', 'required': True}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location', 'required': True}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Required Skills', 'required': True}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salary (e.g. 60000-90000)', 'required': True}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_salary(self):
        salary = self.cleaned_data.get("salary")

        if not salary:
            raise forms.ValidationError("Salary field is required.")

        salary = salary.strip()

        if "-" in salary:
            try:
                start, end = salary.split("-")
                start = int(start.strip())
                end = int(end.strip())
                if start < 0 or end < 0:
                    raise forms.ValidationError("Salary values must be positive numbers.")
                if start >= end:
                    raise forms.ValidationError("Start of the range must be less than the end.")
            except ValueError:
                raise forms.ValidationError("Enter a valid salary range like 60000-90000.")
        else:
            try:
                value = int(salary)
                if value < 0:
                    raise forms.ValidationError("Salary must be a positive number.")
            except ValueError:
                raise forms.ValidationError("Enter a valid salary amount like 90000.")

        return salary


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class SeekerRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Create a UserProfile instance for seeker
            UserProfile.objects.create(user=user, role='seeker')
        return user


class ProviderRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Create a UserProfile instance for provider
            UserProfile.objects.create(user=user, role='provider')
        return user

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['skills', 'qualifications', 'resume']

class EditCompanyProfileForm(forms.ModelForm):
    class Meta:
        model = JobProvider
        fields = ['company_name', 'company_description', 'contact_email', 'website', 'logo']