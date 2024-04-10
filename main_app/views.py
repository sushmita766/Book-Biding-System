import requests
import json
import hmac
import hashlib
import base64
import uuid
from django.db.models import Avg
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from .models import *
from .forms import CategoryForm,BidForm,AuctionForm,OrderForm
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from .decorators import seller_required
from .recommendations import auction_recommendation



#CRUD operation for category starts
@login_required
@seller_required
def category_list(request):
    category_list = Category.objects.all()
    context = {'category_list':category_list}
    return render(request,'main_app/category/category_list.html',context)

@login_required
@seller_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category-list')
    else:
        form = CategoryForm()
        context = {'form':form}
        return render(request,'main_app/category/category_create.html',context)

@login_required
@seller_required  
def category_update(request,pk):
    data = get_object_or_404(Category,id=pk)
    form = CategoryForm(instance=data)
    context = {'form':form}
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=data)
        if form.is_valid():
            form.save()
            return redirect('category-list')
    return render(request,'main_app/category/category_update.html',context)

@login_required
@seller_required
def category_delete(request,pk):
    data = get_object_or_404(Category,id=pk)
    data.is_active=False
    data.save()
    return redirect('category-list')
#Ends category crud

#Auction Crud starts here

@login_required
@seller_required
def auction_list(request):
    auctions = Auction.objects.filter(seller=request.user)
    
    context = {
        'auctions':auctions
    }
    return render(request,'main_app/Auction/auction_list.html',context)


@login_required
@seller_required
def auction_create(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST,request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.save()
            return redirect('auction-list')
    else:
        form = AuctionForm()

    context = {'form': form}
    return render(request, 'main_app/Auction/auction_create.html', context)
    
@login_required
@seller_required
def auction_update(request, pk):
    data = get_object_or_404(Auction, id=pk)

    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            # Handle file field update
            if 'image' in form.changed_data:
                # Clear the existing file
                if data.image:
                    default_storage.delete(data.image.path)
                # Save the new file
                image_file = form.cleaned_data['image']
                data.image.save(image_file.name, ContentFile(image_file.read()))

            form.save()
            return redirect('auction-list')
    else:
        form = AuctionForm(instance=data)

    context = {'form': form, 'auction': data}

    return render(request, 'main_app/Auction/auction_update.html', context)
@seller_required
@login_required
def auction_delete(request,pk):
    data = get_object_or_404(Auction,id=pk)
    data.delete()
    return redirect('auction-list')

#Home page view of the website
@login_required
def home(request):
    if request.user.role == 'Buyer':
        auctions = Auction.objects.filter(auction_status='open')
    else:
        auctions = Auction.objects.all()

    recommended_auctions = auction_recommendation(request)
    # if recommended_auctions:
    #     auctions = list(auctions) + list(recommended_auctions.values())
    
    context = {
        'recommended_auctions':recommended_auctions,
        'auctions':auctions
    }
    return render(request,'main_app/Auction/home.html',context)

@login_required
def homeSearch(request):
    query = request.GET.get('q')
    #storing the query searched by user for using it to recommend items
    if request.user.role == 'Buyer':
        print('yeah')
        UserSearch.objects.create(user=request.user, searchQuery=query)
        auctions = Auction.objects.filter(Q(title__icontains=query) | Q(description__icontains=query),auction_status='open')
    else:
        auctions = Auction.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    
    context = {
        'auctions':auctions
    }
    return render(request,'main_app/Auction/home.html',context)

@login_required
def home_particular_category(request,pk):
    category = get_object_or_404(Category,id=pk)
    if request.user.role == 'Buyer':
        auctions = Auction.objects.filter(auction_status='open',category=category)
    else:
        auctions = Auction.objects.filter(category=category)
    
    context = {
        'category':category,
        'auctions':auctions
    }
    return render(request,'main_app/Auction/home.html',context)


@login_required
def update_auction_status(request, pk):
    data = get_object_or_404(Auction, id=pk)

    if request.method == 'POST':
        data.auction_status == 'closed'
        data.save()
        return JsonResponse({'status':'success','auction_status':data.auction_status})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

@login_required
def auction_detail(request, pk):
    auction = get_object_or_404(Auction, id=pk)
    form = BidForm(request.POST or None)
    user = request.user
    user_highest_bid = get_highest_bid_auction(user.id,auction.id)

    category_avg_price = Auction.objects.filter(category=auction.category).aggregate(Avg('marked_price'))['marked_price__avg']
    print('-----')
    print(category_avg_price)


    if request.method == 'POST':
        if form.is_valid():
            bid_value = form.cleaned_data['bid_value']
            #storing data to use for recommendations
            UserBid.objects.create(user=request.user, auction=auction, bid_value=bid_value, category=auction.category)

            
            if bid_value <= auction.starting_price:
                messages.error(request, 'Bid value must be greater than the starting price.')
            if bid_value <= auction.get_max_bid():
                messages.error(request, 'Bid value must be greater than the current higest price.')
            else:
                bid = form.save(commit=False)
                bid.bidder = request.user
                bid.auction_id = auction
                bid.save()
                
                auction_details = {
                'bid_value': auction.get_max_bid(),
                'bidder':auction.get_higest_bidder(),
                'user_highest_bid':user_highest_bid
                # Add other details as needed
            }

            return JsonResponse(auction_details)
    # Check if an order has already been created for the user and the auction
    existing_order = Order.objects.filter(user=request.user, auction=auction).exists()

    # Create an order if the auction is closed, the user is the winner, and an order doesn't already exist
    if auction.auction_status == 'closed' and auction.winner == request.user and not existing_order:
        order = Order.objects.create(
            user=request.user,
            auction=auction,
            total_amount=auction.get_max_bid(),
            payment_status='pending'
        )

    context = {
        'auction': auction,
        'form': form,
        'user_highest_bid':user_highest_bid,
        'category_avg_price': category_avg_price,
    }

    return render(request, 'main_app/Auction/auction_detail.html', context)
def get_highest_bid_auction(user,auction_id):
        auction = Auction.objects.get(id=auction_id)
        highest_bids = Decimal(0.0)

        user = UserBase.objects.get(id=user)
        max_bid_value = None
        for bid in user.bids.filter(auction_id=auction.id):
            if max_bid_value is None or bid.bid_value > max_bid_value:
                max_bid_value = bid.bid_value
        if max_bid_value is not None:
            highest_bids += max_bid_value
        return highest_bids
@login_required
# def my_order(request):
#     user_id = request.user
#     win_auction = Auction.objects.filter(winner=user_id)
#     total_price = 0
#     for auction in win_auction:
#         price = auction.get_max_bid()
#         total_price += price

#     context = {'auctions':win_auction,'total_price':total_price}
    
#     return render(request,'main_app/Auction/myorder.html',context)
def my_order(request):
    user_orders = Order.objects.filter(user=request.user)
    total_price = sum(order.total_amount for order in user_orders)

    context = {'total_price':total_price,'orders': user_orders}
    
    return render(request,'main_app/Auction/myorder.html',context)

@login_required
def checkout(request):
    user_orders = Order.objects.filter(user=request.user)
    total_price = sum(order.total_amount for order in user_orders)
    form = OrderForm(request.POST )
    if request.method == 'POST':
        if form.is_valid():
            address = form.cleaned_data['address']
            phone_number = form.cleaned_data['phone_number']
            order = FinalOrder.objects.filter(user=request.user,payment_status='pending')
            print(order)
            if order:# to check if user has already make order by  providing address
                return redirect('payment')
            else:
                FinalOrder.objects.create(
                user=request.user,
                address = address,
                phone_number = phone_number,
                total_amount=total_price,
                payment_status='pending'
            )
        return redirect('payment')

    context = {'total_price':total_price,'orders': user_orders,'form':form}
    
    return render(request,'main_app/Auction/checkout.html',context)
@login_required
def makepay(request):
    user_orders = Order.objects.filter(user=request.user)
    total_price = sum(order.total_amount for order in user_orders if order.payment_status == 'pending')
    try:
        final_order = FinalOrder.objects.get(user=request.user, payment_status='pending')
    except FinalOrder.DoesNotExist:
        messages.error(request, 'No pending orders found.')
        context = {'total_price':total_price,'orders': user_orders}
        print(context)
        return render(request, 'main_app/Auction/payment.html',context)

    secret_key = "8gBm/:&EnhH.1/q"
    uuid_val = uuid.uuid4()
    data_to_sign = f"total_amount={total_price},transaction_uuid={uuid_val},product_code=EPAYTEST"
    result = genSha256(secret_key, data_to_sign)

    context = {'total_price':total_price,'orders': user_orders,'order':final_order,'signature':result,'uuid':uuid_val}
    print(user_orders)
    
    return render(request,'main_app/Auction/payment.html',context)

def genSha256(key, message):
        key = key.encode('utf-8')
        message = message.encode('utf-8')

        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        digest = hmac_sha256.digest()
        signature = base64.b64encode(digest).decode('utf-8')

        return signature

def Khalti_initiate(request):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    order = FinalOrder.objects.get(user=request.user)
    
    payload = json.dumps({
        "return_url": "http://127.0.0.1:8000/",
        "website_url": "http://127.0.0.1:8000",
        "amount": float(order.total_amount),
        "purchase_order_id": order.id,
        "purchase_order_name": order.id,
        "customer_info": {
        "name": order.user.username,
        "email": order.user.email,
        "phone": order.user.phone_number
        }
    })
    headers = {
        'Authorization': 'key 497c8f503e724cf4bed3c14506044368',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return JsonResponse("ok",safe=False)

@login_required
def payment_success(request):
    final_order = FinalOrder.objects.get(user=request.user)
    final_order.mark_as_paid()
    user_orders = Order.objects.filter(user=request.user)
    for order in user_orders:
        order.mark_as_paid()

    return redirect('home')
@login_required

def collateral(request):
    current_bids = get_highest_bid(request)#to get current higest bid of user in each auction
    orders = Order.objects.filter(user=request.user)
    utilzed_collateral = sum(order.total_amount for order in orders if order.payment_status=='pending')+current_bids
    total_limit = request.user.collateral*5
    allowed_refund = request.user.collateral - utilzed_collateral
    if request.method == 'POST':
        amount = request.POST.get('collateral')
        return redirect('collateral-load', amount=amount)

    context = {
        'utilized_collateral':utilzed_collateral,
        'total_limit':total_limit,
        'allowed_refund':allowed_refund,
        }
    return render(request,'main_app/Auction/collateral.html',context)

#to get the user higest bid for each auction
def get_highest_bid(request):
    auctions = Auction.objects.all()
    highest_bids = Decimal(0.0)

    user = request.user
    for auction in auctions:
        max_bid_value = None
        for bid in user.bids.filter(auction_id=auction.id):
            if max_bid_value is None or bid.bid_value > max_bid_value:
                max_bid_value = bid.bid_value
        if max_bid_value is not None:
            highest_bids += max_bid_value
    return highest_bids
        

@login_required
def collateral_load(request,amount):
    orders = Order.objects.filter(user=request.user)
    utilzed_collateral = sum(order.total_amount for order in orders)
    total_limit = request.user.collateral*5
    allowed_refund = request.user.collateral - utilzed_collateral
    secret_key = "8gBm/:&EnhH.1/q"
    uuid_val = uuid.uuid4()
    data_to_sign = f"total_amount={amount},transaction_uuid={uuid_val},product_code=EPAYTEST"
    result = genSha256(secret_key, data_to_sign)
    if request.method == 'POST':
        return redirect('collateral-load')
    context = {
        'utilized_collateral':utilzed_collateral,
        'total_limit':total_limit,
        'total_amount':amount,
        'allowed_refund':allowed_refund,
        'signature':result,
        'uuid':uuid_val
        }
    return render(request,'main_app/Auction/load_collateral.html',context)

@login_required
def collateral_success(request,amount):
    # Parse the query parameters from the request URL

    # Convert the total_amount to Decimal
    total_amount = Decimal(amount)

    user = request.user
    user.collateral += total_amount
    user.save()

    return redirect('collateral-home')

@login_required
def collateral_return(request):
    amount = request.POST.get('refund_collateral_amount')
    user = request.user
    if amount:
        user.collateral -= Decimal(amount)
        user.save()
        # Send a success message
        messages.success(request, f"Amount Rs. {amount} has been refunded to your Esewa account.")
    else:
        # Send a warning message if no amount is provided
        messages.warning(request, "No amount provided for refund.")

    return redirect('collateral-home')

@login_required
def calculate_collateral(user_id, orders):
    try:
        order = FinalOrder.objects.get(user=user_id,payment_status='pending')
    except FinalOrder.DoesNotExist:
        order = None
    user = UserBase.objects.get(id=user_id)
    total_price = sum(order.total_amount for order in orders)
    if order:

        collateral = (user.collateral * 5) - total_price
    else:
        collateral = (user.collateral * 5)
    return collateral


    