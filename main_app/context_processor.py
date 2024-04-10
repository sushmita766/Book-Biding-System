from .models import Category,Auction,Order,FinalOrder
from account.models import UserBase
from django.contrib.auth.decorators import login_required
from decimal import Decimal

def categories(request):

    return{
        'categories':Category.objects.all(),
        
    }

def get_detail(request):
    if request.user.is_authenticated:
        user = request.user
        user_id = request.user.id
        try:
            order = FinalOrder.objects.get(user=request.user)
        except FinalOrder.DoesNotExist:
            order = None  # or any other default value you want to set

        orders = get_orders_for_user(user_id)
        collateral = calculate_collateral(user,user_id, orders)
        return {'win_auction': orders, 'collateral': collateral, 'order': order}
    else:
        return {"none": 'none'}
    if request.user.is_authenticated:
        user_id = request.user.id
        order = FinalOrder.objects.get(user=request.user,payment_status='pending')
        orders = get_orders_for_user(user_id)
        collateral = calculate_collateral(user_id, orders)
        return{'win_auction': orders, 'collateral': collateral,'order':order}
    else:
        return{"none": 'none'}

def get_orders_for_user(user_id):
    orders = Order.objects.filter(user=user_id)
    return orders

def calculate_collateral(user,user_id, orders):
    try:
        current_bids = get_highest_bid(user)
        order = FinalOrder.objects.get(user=user_id,payment_status='pending')
    except FinalOrder.DoesNotExist:
        order = None
    user = UserBase.objects.get(id=user_id)
    total_price = sum(order.total_amount for order in orders)
    if order:

        collateral = (user.collateral * 5) - total_price - current_bids
    else:
        collateral = (user.collateral * 5)-current_bids
    return collateral

def get_highest_bid(user_id):
    auctions = Auction.objects.all()
    highest_bids = Decimal(0.0)

    user = user_id
    for auction in auctions:
        max_bid_value = None
        for bid in user.bids.filter(auction_id=auction.id):
            if max_bid_value is None or bid.bid_value > max_bid_value:
                max_bid_value = bid.bid_value
        if max_bid_value is not None:
            highest_bids += max_bid_value
    return highest_bids

# def get_detail(request):
#     if request.user.is_authenticated:
#         user_id = request.user.id

#         win_auction = get_winning_auctions_for_user(request.user)
#         collateral = calculate_collateral(user_id)
#         return{
#             'win_auction':win_auction,
#             'collateral':collateral
#         }
#     else:
#         return {"none":'none'}

# def get_winning_auctions_for_user(user_id):
#     winning_auctions = Auction.objects.filter(winner=user_id)
#     return winning_auctions

# def calculate_collateral(user_id):
#     user = UserBase.objects.get(id=user_id)
#     win_auction = Auction.objects.filter(winner=user_id)
#     total_price = 0
#     for auction in win_auction:
#         price = auction.get_max_bid()
#         total_price += price
#     collateral = (user.collateral * 5) - total_price
#     return collateral