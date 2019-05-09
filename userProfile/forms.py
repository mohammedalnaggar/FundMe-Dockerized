from django import forms
from django.core.exceptions import ValidationError

from .models import UserProfile, ProjectDonations, ProjectComments, ProjectReports
from django.contrib.auth.models import User

from .models import Project, ProjectPics, ProjectTags, ProjectRatings


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(widget=forms.EmailInput, label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

    class Meta():
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used")
        return email


class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfile
        fields = ('firstname', 'lastname', 'profile_pic')


class PasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        # If the user entered the current password, make sure it's right
        if self.cleaned_data['current_password'] and not self.user.check_password(
                self.cleaned_data['current_password']):
            raise ValidationError('This is not your current password. Please try again.')

        # If the user entered the current password, make sure they entered the new passwords as well
        if self.cleaned_data['current_password'] and not (
                self.cleaned_data['password'] or self.cleaned_data['confirm_password']):
            raise ValidationError('Please enter a new password and a confirmation to update.')

        return self.cleaned_data['current_password']

    def clean_confirm_password(self):
        # Make sure the new password and confirmation match
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')

        if password1 != password2:
            raise forms.ValidationError("Your passwords didn't match. Please try again.")

        return self.cleaned_data.get('confirm_password')


class ProjectForm(forms.ModelForm):
    total_target = forms.IntegerField(required=True, min_value=1)
    class Meta:
        model = Project
        details = forms.CharField(widget=forms.Textarea)
        fields = ('category', 'title', 'details', 'start_date', 'end_date', 'total_target')


class ProjectPicsForm(forms.ModelForm):
    project_picture = forms.ImageField(required=False)

    class Meta:
        model = ProjectPics
        fields = ('project_picture',)


class ProjectTagsForm(forms.ModelForm):
    project_tag = forms.CharField(required=False)

    class Meta:
        model = ProjectTags
        fields = ('project_tag',)


class MakeDonationForm(forms.ModelForm):
    donation_amount = forms.IntegerField(required=True, min_value=1)

    class Meta:
        model = ProjectDonations
        fields = ('donation_amount',)


class AddCommentForm(forms.ModelForm):
    comment_body = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = ProjectComments
        fields = ('comment_body',)


class ReportProjectForm(forms.ModelForm):
    report_body = forms.CharField(required=True)

    class Meta:
        model = ProjectReports
        fields = ('report_body',)


class UpdateProfile(forms.ModelForm):
    phone = forms.RegexField(max_length=30, required=False, regex=r'^01[0125][0-9]{8}$', label="Phone")
    country = forms.CharField(required=False, max_length=20, label="Country")
    birthday = forms.DateTimeField(required=False, label="Birthdate YY-M-D")
    profile_pic = forms.ImageField(required=True, label="Profile pic")

    class Meta:
        model = UserProfile
        fields = ('firstname', 'lastname', 'phone', 'profile_pic', 'birthday', 'country')


class RateProjectForm(forms.ModelForm):
    user_rating = forms.IntegerField(required=True, min_value=0, max_value=5)

    class Meta:
        model = ProjectRatings
        fields = ('user_rating',)


class UpdateUser(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label="Username")
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label="Email")

    class Meta:
        model = User
        fields = ('username', 'email')
