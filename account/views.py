from django.shortcuts import render,redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.http import HttpResponse
from .forms import RegistrationForm,SellerRegistrationForm
from django.core.mail import send_mail
from .forms import UserLoginForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .token import account_activation_token
from .models import UserBase
from django.urls import reverse

def buyer_account_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.role = 'Buyer'
            user.is_active = False
            user.is_active=True
            user.save()
            # current_site = get_current_site(request)
            # subject = 'Activate you Account'
            # message = render_to_string('account/account_activation.html',{
            #     'user':user,
            #     'domain':current_site.domain,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':account_activation_token.make_token(user),
            # })
            # res = send_mail(subject,message,'timonbasnet@gmail.com',[user.email])
            # if res:
            #     return render(request,'account/activation.html')
            # else:
            #     return HttpResponse("not send ")
            return redirect(reverse("login"))

            
        else:
            # Form is not valid, render the form with errors
            print(form.errors)
            context = {'form': form}
            return render(request, 'account/buyer_register.html', context)
    else:
        form = RegistrationForm()
        context = {'form': form}
        return render(request, 'account/buyer_register.html', context)
    
def account_activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
        
    except:
        pass
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request,'account/account_activation_invalid.html')

def seller_account_register(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST,request.FILES)
        if form.is_valid():
            print(form.cleaned_data['citizenship'])
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.role = 'Seller'
            user.pan_number = form.cleaned_data['pan_number']
            user.citizenship = form.cleaned_data['citizenship']
            user.is_active = False
            user.save()
            print('----')
            print(user.citizenship)
            messages.success(request,'Your account is uder verification. Stay tuned!')
            return redirect('login')
        else:
            print(form.errors)
            # Form is not valid, render the form with errors
            context = {'form': form}
            return render(request, 'account/seller_register.html', context)
    else:
        form = SellerRegistrationForm()
        print('-----------------')
        context = {'form': form}
        return render(request, 'account/seller_register.html', context)
    
def mail(subject,message,to):
    
    from_email='timonbasnet@gmail.com'

    

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        print(request.POST)
        if form.is_valid():
            print('---')
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')

    else:
        form = UserLoginForm()
    return render(request, 'account/login.html', {'form': form})