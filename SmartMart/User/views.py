from django.shortcuts import render,redirect, get_object_or_404
from . import views
from Guest.models import User 
from vendor.models import Product
from .models import Cart, Order, OrderItem, Feedback, Complaint, Rating
# Create your views here.
def user_home(request):
    return render(request, 'User/User_Home.html')

def profile(request):
    user = User.objects.get(id=request.session['uid'])
    return render(request, 'User/My_Profile.html', {'user':user})


def edit_profile(request):
    user = User.objects.get(id=request.session['uid'])
    message = ""
    if request.method == 'POST':
        user.user_name = request.POST.get('full_name')
        user.user_email = request.POST.get('email')
        user.user_contact = request.POST.get('contact')
        user.user_address = request.POST.get('address')
        if request.FILES.get('photo'):
            user.user_photo = request.FILES.get('photo')
        user.save()
        message = "Profile updated successfully!"
    
    context = {
        "user":user,
        "message": message
    }
        
    return render(request, 'User/Edit_Profile.html', context)

def change_password(request):
    user = User.objects.get(id=request.session['uid'])
    message = ""
    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")
        
        if old == user.user_password:
            if new == confirm:
                user.user_password = new
                user.save()
                message = "Password updated successfully!"
            else:
                message = "New password does not match"
        else:
            message = "Old password incorrect"
            
    context = {
        "user":user,
        "message": message
    }
    return render(request, 'User/Change_Password.html',context)


def search(request):
    products = Product.objects.all()
    return render(request, 'User/Search.html', {'products':products})

def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    
    # 1️⃣ Get logged-in user id from session
    uid = request.session.get("uid")
    
    # Safety check
    if not uid:
        return redirect('guest:login') 
    
    # 2️⃣ Convert id → User object
    user = User.objects.get(id=uid)

    # 3️⃣ Check if product already in cart
    cart = Cart.objects.filter(
        user=user,
        product=product
    ).first()
    
    
    # 4️⃣ Update or create
    if cart:
        cart.quantity += 1
        cart.save()
    else:
        Cart.objects.create(
            user=user,
            product=product,
            quantity=1
        )
    return redirect('user:my_cart')


def my_cart(request):
    if 'uid' not in request.session:
        return redirect('guest:login')

    # 1️⃣ Get user id from session
    user = request.session['uid']
    
    # 2️⃣ Convert id → User instance
    user = User.objects.get(id=user)
    
    # 3️⃣ Use the User instance
    cart_items = Cart.objects.filter(user=user)
    
    # 4️⃣ Calculate total
    total = 0
    for item in cart_items:
        total += item.total_price()
        
    return render(request, 'User/My_Cart.html', {
        'cart_items': cart_items,
        'total': total
    })
    
    

def update_cart_quantity(request, cart_id, action):
    if 'uid' not in request.session:
        return redirect('guest:login')
    
    user = get_object_or_404(User, id=request.session['uid'])
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    
    if action == 'plus': 
        cart.quantity += 1
    elif action == 'minus':
        if cart.quantity > 1:
            cart.quantity -=1
    
    cart.save()
    return redirect('user:my_cart')


def remove_from_cart(request, cart_id):
    if 'uid' not in request.session:
        return redirect('guest:login')
    
    user = get_object_or_404(User, id=request.session['uid'])
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    cart.delete()
    
    return redirect('user:my_cart')

def checkout_view(request):
    # Step 1: get user id from session
    uid = request.session.get('uid')
    
    # Step 2: if user not logged in, go to login page
    if not uid:
        return redirect('guest:login')

    # Step 3: get the logged-in user
    user = User.objects.get(id=uid)
    
    # Step 4: get all cart items of this user
    cart_items = Cart.objects.filter(user=user)
    
    # Step 5: calculate total amount
    total = 0
    for item in cart_items:
        price = int(item.product.price)
        total = total + (price * item.quantity)
        
    # Step 6: send data to template
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'User/checkout.html', context)


def place_order(request):
    # Step 1: get user id from session
    uid = request.session.get('uid')
    
    if not uid:
        return redirect('guest:login')
    
    # Step 2: check form submission
    if request.method == 'POST':
         
        # Step 3: get address from form
        address = request.POST.get('address')
         
        # Step 4: get user
        user = User.objects.get(id=uid)
        
        # Step 5: get cart items
        cart_items = Cart.objects.filter(user=user)
        
        # Step 6: calculate total amount again
        total = 0
        for item in cart_items:
            price = int(item.product.price)
            total = total + (price * item.quantity)
        
        for item in cart_items:
            if item.quantity > item.product.stock:
                return render(request, 'User/My_Cart.html', {
                    'cart_items': cart_items,
                    'total': total,
                    'error': f"Not enough stock for {item.product.product_name}"
                })
            
        # Step 7: INSERT INTO ORDER TABLE ✅
        order = Order.objects.create(
            user = user,
            total_amount = total,
            address = address,
            status="Order Placed"
        )
        
        for item in cart_items:
            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # AUTO STOCK REDUCTION 
            product.stock -= item.quantity
            product.save()
        
        # Step 8: clear cart
        cart_items.delete()
        
        # Step 9: redirect after placing order
        return redirect('user:payment')
    
    return redirect('user:checkout')

def payment(request):
    uid = request.session.get('uid')
    
    if not uid:
        return redirect('guest:login')
    user = User.objects.get(id=uid)
    order = Order.objects.filter(user=user).last()
    
    if request.method == "POST":
        order.status = "completed"
        order.save()
        
        # redirect after successful payment
        return redirect('user:order_success')
    
    # When page is loaded normally
    return render(request, 'User/Payment.html', {'order':order})


def order_success(request):
    uid = request.session.get('uid')
    message=""

    if not uid:
        return redirect('guest:login')
    
    return render(request, 'User/PaymentSuccess.html')


def order_list(request):
    uid = request.session.get('uid')

    if not uid:
        return redirect('guest:login')
    
    user = User.objects.get(id=uid)
    orders = Order.objects.filter(user=user).order_by('-id')
    return render(request, 'User/OrderList.html', {
        'orders': orders
    })
    
def order_detail(request, order_id):
    uid = request.session.get('uid')

    if not uid:
        return redirect('guest:login')

    user = User.objects.get(id=uid)

    # get order (only if it belongs to this user)
    order = get_object_or_404(Order, id=order_id, user=user)

    # get items using related_name="items"
    items = order.items.all()

    return render(request, 'User/OrderDetail.html', {
        'order': order,
        'items': items
    })


def add_feedback(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('guest:login')
    
    message = ""
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        Feedback.objects.create(
            user_id=uid,
            title=title,
            content=content
        )
        message = "Feedback saved successfully"
    
    feedbacks = Feedback.objects.filter(user_id=uid).order_by('-created_at')
    context = {
        'feedbacks':feedbacks,
        'message':message
    }
    return render(request, 'User/Feedback.html', context)


def add_complaint(request):
    
    uid = request.session.get('uid')
    if not uid:
        return redirect('guest:login')
    
    message = ""
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        Complaint.objects.create(
            title = title,
            content = content,
            user_id=uid,
            status = 'completed'
        )
        message = "Complaint saved successfully"
    complaints = Complaint.objects.filter(user_id=uid).order_by('-created_at')
    context = {
        'complaints':complaints,
        'message':message
    }
    return render(request, 'User/Complaint.html', context)


def rating(request, product_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('guest:login')

    user = User.objects.get(id=uid)
    product = Product.objects.get(id=product_id)

    message = ""
    existing_rating = Rating.objects.filter(
        user=user,
        product=product
    ).first()

    if request.method == 'POST':
        stars = request.POST.get('rating')
        review = request.POST.get('review')

        if not stars:
            message = "Please select a rating"
        else:
            existing_rating, created = Rating.objects.update_or_create(
                user=user,
                product=product,
                defaults={
                    'rating': stars,
                    'review': review
                }
            )
            message = "Thank you for your rating!"

    return render(request, 'User/Rating.html', {
        'product': product,
        'existing_rating': existing_rating,
        'user': user,
        'message': message
    })




def logout(request):
    del request.session['uid']
    return redirect("guest:index")
    

