from django import forms

class LoginForm(forms.Form):
   username = forms.CharField()
   password = forms.CharField()

class RegisterForm(forms.Form):
   username = forms.CharField()
   password = forms.CharField()
   email = forms.EmailField()

class ChangePasswordForm(forms.Form):
   password = forms.CharField()

class RecoveryForm(forms.Form):
   email = forms.EmailField()

class ContactForm(forms.Form):
   sender = forms.EmailField()
   message = forms.CharField(widget=forms.Textarea)

class PlaylistForm(forms.Form):
   name = forms.CharField(max_length=50)
   comment = forms.CharField(widget=forms.Textarea, required=False)

class ProfileForm(forms.Form):
   first_name = forms.CharField(required=False)
   last_name = forms.CharField(required=False)
   email = forms.EmailField()
   auth_key = forms.CharField(required=False)
