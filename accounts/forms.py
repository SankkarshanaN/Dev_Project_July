from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "Enter email",
        "class": "form-control"
    }))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Enter username",
            "class": "form-control"
        })
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Enter password",
            "class": "form-control"
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Confirm password",
            "class": "form-control"
        })
