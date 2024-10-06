"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import *


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class ExistingAthleteRegistrationForm(forms.ModelForm):
     classes = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),  # Changed 'classes' to 'class'
        label="Select Class",
         )

     class Meta:
        model = Registration
        exclude = ['created_by', 'description', 'athlete', 'class_id', 'status']

     def __init__(self, *args, **kwargs):
        club = kwargs.pop('club', None)
        super(ExistingAthleteRegistrationForm, self).__init__(*args, **kwargs)
        if club:
            # Filter the classes based on the club's current active season
            active_season = Season.objects.filter(club=club, is_active=True).first()
            if active_season:
                self.fields['classes'].queryset = Class.objects.filter(season=active_season)
                
class AthleteRegistrationForm(forms.ModelForm):
    class Meta:
        model = Athlete
        exclude = ['created_by', 'description', 'club']

    def __init__(self, *args, **kwargs):
        super(AthleteRegistrationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = f'Enter {field.label}'  
            field.widget.attrs['Class'] = 'form-control' 


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        exclude = ['created_by', 'description', 'athlete', 'class_id', 'status']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = f'Enter {field.label}' 
            field.widget.attrs['class'] = 'form-control'
            

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        exclude = ['created_by']
        
        # Add custom widgets for better user experience
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'days_of_week': forms.CheckboxSelectMultiple(),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # Optional: Custom validation if needed
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'End date must be after start date.')

        return cleaned_data
    
class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = User
        exclude = ['created_by']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password