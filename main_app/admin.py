from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Product)
admin.site.register(UserBid)
admin.site.register(UserSearch)
admin.site.register(Order)
admin.site.register(FinalOrder)
