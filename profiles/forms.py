# forms.py
from django import forms
from .models import Member

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control',
                'id': 'id_profile_picture'
            })
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Image file too large ( > 5MB )')
            if not picture.content_type.startswith('image'):
                raise forms.ValidationError('File is not an image')
        return picture