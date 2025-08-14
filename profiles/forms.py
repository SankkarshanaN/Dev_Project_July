from django import forms
from .models import Member

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['profile_picture']
