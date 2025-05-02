from django import forms
from django.contrib.auth.models import User
from .models import Job, JobApplication, UserProfile, JobProvider, JobSeeker, JobCustomQuestion, JobApplication, JobApplicationAnswer
from django import forms
from .models import Job
from django.forms import inlineformset_factory
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'location', 'skills', 'salary', 'job_type', 'experience_level', 'logo','last_date_to_apply']        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Job Description', 'required': True}),
            'company': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Company Website URL', 'required': True}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location', 'required': True}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Required Skills', 'required': True}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salary (e.g. 60000-90000)', 'required': True}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'last_date_to_apply': forms.DateInput(attrs={'type': 'date'}),
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
            UserProfile.objects.create(user=user, role='provider')
        return user

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['skills', 'qualifications', 'resume']

class EditCompanyProfileForm(forms.ModelForm):
    class Meta:
        model = JobProvider
        fields = ['company_name', 'company_description', 'contact_email', 'website','company_logo', 'phone', 'location']    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields except company_name optional
        self.fields['company_description'].required = False
        self.fields['contact_email'].required = False
        self.fields['website'].required = False
    
    def clean_company_logo(self):
        logo = self.cleaned_data.get('company_logo')
        if logo:
            if logo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2MB )")
            if not logo.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError("Unsupported file type. Please upload a JPG or PNG image.")
        return logo
    
class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeeker
        fields = ['full_name', 'email', 'phone', 'address','location_preferences', 'education', 
                  'experience_years', 'skills', 'resume', 'profile_picture', 
                  'linkedin', 'about_me', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'skills': forms.Textarea(attrs={'placeholder': 'Enter your skills separated by commas (e.g., Python, JavaScript, Project Management)'}),
            'education': forms.Textarea(attrs={'placeholder': 'Describe your education background'}),
            'about_me': forms.Textarea(attrs={'placeholder': 'Write a short bio about yourself'}),
        }
class CustomQuestionForm(forms.ModelForm):
    class Meta:
        model = JobCustomQuestion
        fields = ['question_text', 'question_type', 'is_required']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question Text'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Create a formset for adding multiple custom questions
CustomQuestionFormSet = inlineformset_factory(
    Job, 
    JobCustomQuestion, 
    form=CustomQuestionForm,
    extra=1, 
    can_delete=True
)
class TextAnswerForm(forms.Form):
    answer = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

class YesNoAnswerForm(forms.Form):
    answer = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))

class FileAnswerForm(forms.Form):
    answer = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))

class LinkAnswerForm(forms.Form):
    answer = forms.URLField(widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter a valid URL (e.g., https://...)'
    }))