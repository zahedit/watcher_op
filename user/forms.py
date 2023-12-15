from typing import Any, Dict
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserChangeForm
User = get_user_model()

#############################################
class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        if User.objects.filter(username = self.cleaned_data['username']).exists():
            raise forms.ValidationError(_("Username already exists"))
        if User.objects.filter(email = self.cleaned_data['email']).exists():
            raise forms.ValidationError(_("Email address already exists"))
        
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("The passwords do not match.")
            
        if len(password) < 8:
            raise forms.ValidationError("The new password must be at least 8 characters long.")
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            raise forms.ValidationError("The new password must contain at least one letter and at least one digit or" \
                                            " punctuation character.")
        return self.cleaned_data
    
    def save(self):
        self.cleaned_data.pop("confirm_password", None)
        user = User.objects.create_user(**self.cleaned_data) #create_user => hash the password
        return user
###########################################
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        user = User.objects.filter(username = self.cleaned_data['username']).first()
        if user is None:
            raise forms.ValidationError(_("Username doesn't exists"))
        
        # if not user.check_password(self.cleaned_data['password']):
        #     raise forms.ValidationError(_("Wrong password"))

        user = authenticate(**self.cleaned_data)
        if user is None:
            raise forms.ValidationError(_("Unable to login with provided credentials"))

        self.cleaned_data['user'] = user
        return self.cleaned_data
#############################################
class UserUpdateForm(UserChangeForm):
    # Specify the fields that you want to update
    username = forms.CharField(max_length=150, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    email = forms.EmailField()
    nickname = forms.CharField(max_length=150, required=False)
    phone_number = forms.CharField(max_length=11, required=False)
    avatar = forms.ImageField(required=False)
    bio = forms.Textarea()
    website = forms.URLField(required=False)

    class Meta:
        model = User
        # Specify the fields that you want to display in the form
        fields = ("username", "email", "nickname", "phone_number", "avatar", "bio", "website")

    def __init__(self, *args, **kwargs):
        # Get the current user from the kwargs
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Check if the user is admin
        if not user.is_staff:
            # If not, disable the username field
            self.fields["username"].disabled = True

    def clean_username(self):
        # Validate the username field
        username = self.cleaned_data["username"]
        # Check if the username is already taken by another user
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        # Validate the email field
        email = self.cleaned_data["email"]
        # Check if the email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
#############################################