from django import forms
from django.contrib.auth.models import User
from ABapp.models import Userinfo,AB_troubleshooting,AB_data,AB_sitestatus

class Registrationinfo(forms.ModelForm):
    password = forms.CharField(max_length=20, min_length=5, widget=(forms.PasswordInput()))
    class Meta:
        model = User
        fields = ('username','email','password')
        help_texts = {
            'username': None,
        }

class Registrationdata(forms.ModelForm):
    class Meta:
        model = Userinfo
        fields = ('team_name',)

class ABstore(forms.ModelForm):
    class Meta:
        model = AB_troubleshooting
        fields = '__all__'

class ABstoredata(forms.ModelForm):
    class Meta:
        model = AB_data
        fields = ('asin','buyability_status')

class ABsitestatus(forms.ModelForm):
    class Meta:
        model = AB_sitestatus
        fields = '__all__'
