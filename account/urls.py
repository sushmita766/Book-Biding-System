from django.urls import path
from django.contrib.auth import views as auth_views
from .import views
from .forms import UserLoginForm

urlpatterns = [
    path('register_seller',views.seller_account_register,name='seller-register'),
    path('register_buyer',views.buyer_account_register,name='buyer-register'),
    path('activate/<slug:uidb64>/<slug:token>/',views.account_activate, name='activate'),
    path('login/',auth_views.LoginView.as_view(template_name='account/login.html',form_class=UserLoginForm),name='login'),
    #path('login/',views.user_login,name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page="/account/login/"),name='logout'),
    path('mail/',views.mail)
]
