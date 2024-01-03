from django import forms
from .models import *
from django.contrib.auth.models import User

# save new user.
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


# update user profile.
class ProfileSettings(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_status', 'profile_photo']


# add new post.
class AddPost(forms.ModelForm):
    class Meta:
        model = UserPost
        fields = ['media', 'description']


# add comment to the post.
class CommentForm(forms.ModelForm):
    class Meta:
        model = UserComment
        fields = ['comment']

