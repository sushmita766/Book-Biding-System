from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

class UserManager(BaseUserManager):
    
    def create_user(self,email,username,password,**other_fileds):
        if not email:
            raise ValueError('You must provide an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,username=username,**other_fileds) # self.model is a way to dynamically reference the model class that this custom manger is associated
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email,username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email,username,password, **extra_fields)


class UserBase(AbstractBaseUser,PermissionsMixin):

    ROLE_CHOICES = (
    ('Buyer','Buyer'),
    ('Seller','Seller'),
    )
    username = models.CharField(max_length=100,blank=True)
    pan_number = models.CharField(max_length=100, blank=True, default=0)
    citizenship  = models.ImageField(upload_to='images/',blank=True)
    email = models.EmailField(unique=True)
    firstname  = models.CharField(max_length=100,blank=True)
    phone_number = models.CharField(max_length=10,blank=True)
    address = models.CharField(max_length=250,blank=True)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)
    collateral = models.DecimalField(max_digits=50, decimal_places=2,default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

