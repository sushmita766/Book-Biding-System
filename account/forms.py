from django import forms
from .models import UserBase
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Enter Username',min_length=4,max_length=50,help_text='*Required')
    email = forms.EmailField(max_length=100,help_text='*Required',error_messages={'required':'Please enter your email'})
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=10,min_length=10)

    class Meta:
        model = UserBase
        fields = ('username','email','phone_number')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control mb-1',})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control mb-1', 'name': 'email', 'id': 'id_email'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control mb-1', })
        self.fields['phone_number'].widget.attrs.update(
            {'class': 'form-control mb-1',})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control mb-1',})
        

class SellerRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Username',min_length=4,max_length=50,help_text='*Required')
    email = forms.EmailField(max_length=100,help_text='*Required',error_messages={'required':'Please enter your email'})
    pan_number = forms.CharField(label="Pan Number",max_length=100,min_length=5)
    citizenship  = forms.ImageField(label="Cetizenship photo")
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=10,min_length=10)

    class Meta:
        model = UserBase
        fields = ('username','email','phone_number')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control mb-1',})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control mb-1', 'name': 'email', 'id': 'id_email'})
        self.fields['pan_number'].widget.attrs.update(
            {'class': 'form-control mb-1', })
        self.fields['citizenship'].widget.attrs.update(
            {'class': 'form-control mb-1', })
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control mb-1', })
        self.fields['phone_number'].widget.attrs.update(
            {'class': 'form-control mb-1',})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control mb-1',})


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.update(
            {'class':'form-control mb-1'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control mb-1', })

