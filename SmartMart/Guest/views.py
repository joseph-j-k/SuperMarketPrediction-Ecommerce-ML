from django.shortcuts import render, redirect
from .models import User, Seller
from administrator.models import Place, District, Admin
# Create your views here.
def index(request):
    return render(request, "index.html")

def user_register(request):
    district=District.objects.all()
    message = ""
    context = {
        'district':district,
        'message':message
    }
    if request.method == "POST":
        place = Place.objects.get(id=request.POST.get("sel_place"))
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        address = request.POST.get("address") 
        password = request.POST.get("password")
        photo=request.FILES.get("photo") 
        User.objects.create(
            user_name = full_name, 
            user_email = email,
            user_contact = contact,
            user_address = address,
            user_password = password,
            user_photo = photo,
            place = place,
        )
        context['message'] = "User registered successfully"
    return render(request, 'Guest/UserRegistration.html', context)


def seller_registration(request):
    district=District.objects.all()
    message = ""
    context = {
        'district':district,
        'message':message
        }
    if request.method == "POST":
        place = Place.objects.get(id=request.POST.get("sel_place"))
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        address = request.POST.get("address") 
        password = request.POST.get("password")
        photo = request.FILES.get("photo")
        proof = request.FILES.get("proof")
        Seller.objects.create(
            seller_name = full_name,
            seller_email = email,
            seller_contact = contact,
            seller_address = address,
            seller_password = password,
            seller_photo = photo,
            seller_proof = proof,
            place = place,
        )
        message = "Seller registered successfully"
    return render(request, 'Guest/SellerRegistration.html', context)


def ajax_place(request):
    place = Place.objects.filter(district=request.GET.get('did'))
    return render(request, 'Guest/AjaxPlace.html',{'place':place})


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        userCount = User.objects.filter(user_email=email, user_password=password).count()
        adminCount = Admin.objects.filter(admin_email=email, admin_password=password).count()
        sellerCount = Seller.objects.filter(seller_email=email, seller_password=password).count()
        
        if userCount > 0:
            user = User.objects.get(user_email=email, user_password=password)
            request.session['uid'] = user.id
            return redirect('user:user_home')

        elif adminCount > 0:
            admin  = Admin.objects.get(admin_email=email, admin_password=password)
            request.session['aid'] = admin.id
            return redirect('admin_pannel:dashboard')
        
        elif sellerCount > 0:
            seller = Seller.objects.get(seller_email=email, seller_password=password)
            request.session['sid'] = seller.id
            return redirect('vendor:vendor_home')
        
    return render(request, 'Guest/Login.html')