from django.contrib.auth.decorators import login_required
from django.db import transaction

from paymentservice.models import User, Order, RefundOrder
from rest_framework.decorators import api_view
from datetime import datetime
import random
from django.http.response import JsonResponse
import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


@api_view(['POST'])
def Register(request):
    if request.method == 'POST':
        # name = request.POST.get('Name')
        # email = request.POST.get('Email')
        # password = request.POST.get('Password')
        data = json.loads(request.body)
        name = data.get('Name')
        email = data.get('Email')
        password = data.get('Password')
        print(name, email, password)
        if not all([name, email, password]):
            return JsonResponse({'error': 'Invalid input'}, status=400)
        user = User.objects.create(name=name, password=password, email=email, balance=0)
        if user:
            return JsonResponse({'AccountID': user.id, 'Name': name})
        return JsonResponse({'error': 'Failed to create user'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['POST'])
def Login(request):
    
    if request.method == 'POST':
        try:
            # id = request.POST.get('ID')
            # password = request.POST.get('Password')
            data = json.loads(request.body)
            print(data)
            id = data.get('ID')
            password = data.get('Password')
            user = User.objects.filter(id=id).first()
            if user and password == user.password:
                request.session['user_id'] = user.id
                return JsonResponse('Success', status=200,safe= False)
        except:
            return HttpResponse('Invalid credentials', status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['POST'])
def Orders(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # user_id = data.get('user_id')
        if not request.session.get('user_id'):
            return JsonResponse({'error': 'You are not authorized to perform this action. Please log in and try again.'}, status=401)
               
        # merchant_order_id = request.data.get('MerchantOrderId')
        merchant_order_id = data.get('MerchantOrderId')
        # price = request.data.get('Price')
        price = data.get('Price')
        
        if not merchant_order_id or not price:
            return JsonResponse({'error': 'Invalid format. Please provide MerchantOrderId and Price in request body.'}, status=400)
        to_account = request.session['user_id']
        stamp = str(int(datetime.now().timestamp())) + str(random.randint(1000, 9999))
        order = Order.objects.create(
            merchant_order_id=merchant_order_id,
            order_time=datetime.now(),
            price=price,
            stamp=stamp,
            to_account=to_account
        )
        if order:
            return JsonResponse({'PaymentId': order.id, 'Stamp': order.stamp})
        return JsonResponse({'error': 'Failed to create order. Please try again.'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['POST'])
def Pay(request):
    data = json.loads(request.body)
    payment_id = data.get('PaymentId')
    # payment_id = request.POST.get('PaymentId')
    if not request.session.get('user_id'):
            return JsonResponse({'error': 'You are not authorized to perform this action. Please log in and try again.'}, status=401)
    try:
        order = Order.objects.get(id=payment_id)
        from_account = User.objects.get(id=request.session['user_id'])
        if from_account.balance < order.price:
            return JsonResponse({'error': 'Not enough balance'}, status=400, safe=False)
        to_account = User.objects.get(id=order.to_account)
        from_account.balance -= order.price
        to_account.balance += order.price
        order.from_account = from_account.id
        order.payment_time = datetime.now()
        order.save()
        from_account.save()
        to_account.save()
        return JsonResponse({'Stamp': order.stamp})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Invalid PaymentId'}, status=400, safe=False)
    return JsonResponse({'error': 'Unauthorized'}, status=401, safe=False)


@api_view(['POST'])
def Refund(request):
    data = json.loads(request.body)
    payment_id = data.get('PaymentId')
    price = int(data.get('Price'))
    # payment_id = request.POST.get('PaymentId')
    # price = int(request.POST.get('Price'))
    try:
        order = Order.objects.get(id=payment_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=400)

    refund_orders = RefundOrder.objects.filter(payment_id=payment_id)
    total_refund_amount = sum(refund.price for refund in refund_orders)

    if total_refund_amount + price > order.price:
        return JsonResponse({'error': 'Refund amount exceeds the order price'}, status=400)

    from_account = User.objects.get(id=request.session['user_id'])
    to_account = User.objects.get(id=order.to_account)

    if from_account.balance < price:
        return JsonResponse({'error': 'Insufficient balance'}, status=400)

    with transaction.atomic():
        # Update the balance of the two accounts
        from_account.balance -= price
        from_account.save()
        to_account.balance += price
        to_account.save()

        # Create the refund order
        RefundOrder.objects.create(payment_id=payment_id, price=price)

    return JsonResponse({'message': 'Refund success'}, status=200)


@api_view(['GET'])
def Balance(request):
    user_id = request.session.get('user_id')
    balance = User.objects.get(id=user_id).balance
    return JsonResponse({'Balance': balance})


@api_view(['POST'])
def Deposit(request):
    user = User.objects.get(id=request.session.get('user_id'))
    # price = request.POST.get('Price')
    data = json.loads(request.body)
    price = data.get('Price')
    if not price:
        return JsonResponse({'error': 'Price is required.'}, status=400)
    try:
        price = int(price)
        if price <= 0:
            return JsonResponse({'error': 'Price must be a positive integer.'}, status=400)
        user.balance += price
        user.save()
        return JsonResponse({'message': 'Deposit succeeded.'})
    except ValueError:
        return JsonResponse({'error': 'Price must be a positive integer.'}, status=400)