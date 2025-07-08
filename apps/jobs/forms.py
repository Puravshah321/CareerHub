from django import forms
from .models import Job, Application, Category

class JobForm(forms.ModelForm):
    job_type = forms.ChoiceField(choices=Job.JOB_TYPE_CHOICES)
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'requirements',
            'location', 'salary', 'job_type', 'deadline'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Write your cover letter here...',
                    'required': 'required',  # Client-side enforcement
                }
            )
        }

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if not cover_letter or cover_letter.strip() == '':
            raise forms.ValidationError("Cover letter cannot be empty.")
        return cover_letter
    
    
class JobSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Job title or keyword'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location'})
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES
    )
    posted_date = forms.ChoiceField(
    choices=[
        ('', 'All'),
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
    ])
    
class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'salary', 'job_type', 'deadline', 'category']
        
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'description', 'requirements', 'location', 'salary', 'job_type', 'deadline', 'is_active']