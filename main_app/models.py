from django.db import models
from django.urls import reverse
from bidandbuy.settings import AUTH_USER_MODEL
from account.models import UserBase
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.db.models import Max
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Category(models.Model):

    IS_ACTIVE_CHOICES = (
    (True, 'Active'),
    (False, 'Inactive'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(choices=IS_ACTIVE_CHOICES,default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    discount = models.IntegerField(
        validators = [MinValueValidator(0),MaxValueValidator(99)]
    )
    actual_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    
    def save(self, *args, **kwargs):
        price_decimal = Decimal(str(self.price))
        self.actual_price = price_decimal - (Decimal(str(self.discount)) / 100)*price_decimal
        super(Product,self).save(*args,**kwargs)

    def __str__(self):
        return self.title

class Auction(models.Model):

    def clean(self):
        """
        Custom validation to ensure start_datetime is before end_datetime.
        """
        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValidationError("Start datetime must be before end datetime.")
        
        now = timezone.now()

        if now < self.start_datetime:
            self.auction_status = 'draft'
        elif self.start_datetime <= now <= self.end_datetime:
            self.auction_status = 'open'
        elif now > self.end_datetime:
            self.auction_status = 'closed'
            self.set_winner()

    AUCTION_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'open'),
        ('closed', 'Closed'),
    )
    

    winner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,editable=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    marked_price = models.DecimalField(max_digits=10, decimal_places=2)
    auction_status = models.CharField(max_length=20, choices=AUCTION_STATUS_CHOICES, default='draft')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    seller = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auctions')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
   
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Auctions'

    def get_absolute_url(self):
        return reverse("auction-detail", args=[self.pk])
    
    def get_max_bid(self):
        return Bid.get_max_bid_for_auction(self.id)
    
    def get_higest_bidder(self):
        return Bid.get_highest_bidder_name(self.id)
    
    def get_remaining_time(self):
        now = timezone.now()

        if now < self.start_datetime:
            return "Auction has not started yet."
        elif now > self.end_datetime:
            return "Auction has ended."

        remaining_time = self.end_datetime - now
        return remaining_time
    
    def set_winner(self):
        highest_bidder = Bid.get_highest_bidder_name(self.id)
        if highest_bidder:
            highest_bidder = UserBase.objects.get(username=highest_bidder)
            self.winner = highest_bidder
        else:
            self.winner = None

def update_auction_status(sender, instance, **kwargs):
    now = timezone.now()

    if now < instance.start_datetime:
        instance.auction_status = 'draft'
    elif instance.start_datetime <= now <= instance.end_datetime:
        instance.auction_status = 'open'
    elif now > instance.end_datetime:
        instance.auction_status = 'closed'
        instance.set_winner()

pre_save.connect(update_auction_status, sender=Auction)

class Bid(models.Model):
    bidder = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid_listing")
    bid_value = models.DecimalField(max_digits=10, decimal_places=2)
    bid_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.bid_value)

    def get_highest_bidder_name(auction_id):
        max_bid = Bid.objects.filter(auction_id=auction_id).order_by('-bid_value').first()
        highest_bidder = max_bid.bidder.username if max_bid else None

        return highest_bidder

    @staticmethod
    def get_max_bid_for_auction(auction_id):
        max_bid = Bid.objects.filter(auction_id=auction_id).aggregate(Max('bid_value'))['bid_value__max']
        return max_bid or 0
    

class UserSearch(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    searchQuery = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class UserBid(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    bid_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'pending'),
        ('paid and shipped', 'paid and shipped'),
    )
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices = PAYMENT_STATUS_CHOICES, default='pending')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"

    def mark_as_paid(self):
        self.payment_status = 'paid and shipped'
        self.save()

class FinalOrder(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'pending'),
        ('paid and shipped', 'paid and shipped'),
    )
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices = PAYMENT_STATUS_CHOICES, default='pending')    
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Final Order #{self.pk} - {self.user.username}"
    
    def mark_as_paid(self):
        self.payment_status = 'paid and shipped' 
        self.save()
