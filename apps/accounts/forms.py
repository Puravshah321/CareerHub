from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import CustomUser, Employer, JobSeeker

# Choices for Job Seeker Interests
INTEREST_CHOICES = [
    ('Programming', 'Programming'),
    ('Business and Management', 'Business and Management'),
    ('Web Development', 'Web Development'),
    ('Database Management', 'Database Management'),
    ('Technical', 'Technical'),
    ('Law', 'Law'),
    ('Other Specialized Areas', 'Other Specialized Areas'),
]

def validate_password_strength(password):
    import re
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[\W_]', password):
        raise ValidationError("Password must contain at least one special character.")


class EmployerSignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z@.+\-_]+$',
                message="Username may contain only letters and @/./+/-/_ characters (no digits allowed)."
            )
        ]
    )

    email = forms.EmailField()
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password_strength]
    )
    password2 = forms.CharField(widget=forms.PasswordInput)

    company_name = forms.CharField(
        max_length=150,
        min_length=3
    )
    company_description = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    company_website = forms.URLField()
    company_logo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_company_logo(self):
        logo = self.cleaned_data.get('company_logo')
        if logo and logo.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise forms.ValidationError("Only JPEG, PNG, and JPG files are allowed.")
        return logo

    def clean_company_name(self):
        name = self.cleaned_data.get('company_name')
        if not (3 <= len(name.strip()) <= 150):
            raise forms.ValidationError("Company name must be between 3 and 150 characters.")
        return name

    def clean_company_website(self):
        website = self.cleaned_data.get('company_website')
        if website and not website.startswith(('http://', 'https://')):
            raise forms.ValidationError("Enter a valid website URL starting with http:// or https://")
        return website

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_employer = True
        if commit:
            user.save()
            Employer.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name'),
                company_description=self.cleaned_data.get('company_description'),
                company_website=self.cleaned_data.get('company_website'),
                company_logo=self.cleaned_data.get('company_logo')
            )
        return user


class JobSeekerSignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z@\-]+$',
                message="Username may contain only letters, @, and - characters."
            )
        ]
    )
    email = forms.EmailField()
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password_strength]
    )
    password2 = forms.CharField(widget=forms.PasswordInput)

    skills = forms.CharField(widget=forms.Textarea, required=True)
    resume = forms.FileField(required=True)
    experience = forms.CharField(widget=forms.Textarea, required=True)
    education = forms.CharField(widget=forms.Textarea, required=True)
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if not resume.name.lower().endswith('.pdf'):
                raise ValidationError("Resume must be a PDF file.")
            if resume.content_type != 'application/pdf':
                raise ValidationError("Uploaded file is not a valid PDF.")
        return resume

    def clean_interests(self):
        interests = self.cleaned_data.get('interests')
        if interests and len(interests) > 3:
            raise ValidationError("You can select up to 3 areas of interest.")
        return interests
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_job_seeker = True
        if commit:
            user.save()
            JobSeeker.objects.create(
                user=user,
                skills=self.cleaned_data.get('skills'),
                resume=self.cleaned_data.get('resume'),
                experience=self.cleaned_data.get('experience'),
                education=self.cleaned_data.get('education')
            )
        return user

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeeker
        fields = ['resume', 'skills', 'experience', 'education']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.Textarea(attrs={'rows': 3}),
            'education': forms.Textarea(attrs={'rows': 3}),
        }