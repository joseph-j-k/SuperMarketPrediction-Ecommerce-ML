from django.shortcuts import render,redirect, get_object_or_404
from .models import District, Place, Category, SubCategory, Admin
from User.models import Complaint, Feedback, OrderItem 
from vendor.models import Product
from Guest.models import Seller, User
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
import json


def dashboard(request):
    users = User.objects.select_related('place__district').all()
    categories = Category.objects.all()[:20]
    context = {
        'total_users': User.objects.count(),
        'total_vendors': Seller.objects.count(),
        'total_admins': Admin.objects.count(),
        'total_category': Category.objects.count(),
        'users': users, 
        'categories': categories,
    }
    return render(request, 'admin/Dashboard.html', context)


def district(request):
    message = "" 
    
    if request.method == "POST":
        district_name = request.POST.get("district")
        if district_name:
            District.objects.create(district_name = district_name)
            message = "District saved successfully"
    districts = District.objects.all()
    
    context = {
        "districts": districts,
        "message": message
        }
    return render(request, 'admin/District.html', context)

def district_edit(request, id):
    district = get_object_or_404(District, id=id)
    message = ""
    
    if request.method == "POST":
        district_name = request.POST.get("district")
        if district_name:
            district.district_name=district_name
            district.save()
            message = "District updated successfully"
    districts = District.objects.all()
    
    context = {
        "districts": districts,
        "district": district,
        "message": message
        }
    return render(request, 'admin/District.html', context)

def district_delete(request, id):
    district = get_object_or_404(District, id=id)
    district.delete()
    
    districts = District.objects.all()

    context = {
        "districts": districts,
        "message": "District deleted successfully"
    }
    return render(request, "admin/District.html", context)


def place(request):
    message = "" 
    if request.method == 'POST':
        district_id = request.POST.get('district_id')
        place_name = request.POST.get('place_name')
        
        district = District.objects.get(id=district_id)
        Place.objects.create(
            district=district,
            place_name=place_name
        )
        message = "Place saved successfully"
    districts = District.objects.all()
    places = Place.objects.all()
    context = {
        'districts': districts,
        'places': places,
        "message": message
    }
    return render(request, 'admin/Place.html', context)


def place_edit(request, id):
    message = "";
    
    # get the place to edit
    place = Place.objects.get(id=id)
    
    if request.method == 'POST':
        district_id = request.POST.get('district_id')
        place_name = request.POST.get('place_name')
        
        # update values
        place.district_id = district_id
        place.place_name = place_name
        place.save()
        
        message = "Place updated successfully"
        
    # load districts for dropdown
    districts = District.objects.all()
    context = {
        'place':place,
        'districts': districts,
        'places': Place.objects.all(),
        'message': message
    }
    
    return render(request, 'admin/Place.html', context)


def place_delete(request, id):
    message = "";
    
    # get the place
    place = Place.objects.get(id=id)
    
    # delete the place
    place.delete()
    message = "Place deleted successfully"
    
    # reload data
    districts = District.objects.all()
    places = Place.objects.all()
    
    context = {
        'districts': districts,
        'places': places,
        'message': message
    }
    return render(request, 'admin/Place.html', context)


def category(request):
    message = "";
    if request.method == "POST":
        category_name = request.POST.get('category')    
        if category_name:
            Category.objects.create(category_name=category_name)
            message = "Category saved successfully"
    categorys = Category.objects.all()
    contenct = {
        'categorys':categorys,
        'message':message 
    }
    return render(request, 'admin/Category.html', contenct)


def category_edit(request, id):
    category = Category.objects.get(id=id)
    message = "";
    
    if request.method == "POST":
        category_name = request.POST.get('category')
        if category_name:
            category.category_name = category_name
            category.save()
            message = "Category updated successfully"       
    categorys = Category.objects.all()
    
    context = {
        'categorys':categorys,
        'category':category,
        'message':message
    }
    return render(request, 'admin/Category.html', context)

def category_delete(request, id):
    message = ""
    category = Category.objects.get(id=id)
    category.delete()
    
    categorys = Category.objects.all()
    message = "Category deleted successfully"
    
    context = {
        'categorys':categorys,
        'message':message
    }
    return render(request, 'admin/Category.html', context)

def sub_category(request):
    message = ""
    
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        subcategory_name = request.POST.get('sub_category')
        
        category = Category.objects.get(id=category_id)
        SubCategory.objects.create(
            category = category,
            subcategory_name = subcategory_name
        )
        message = "Subcategory saved successfully"
        
    categorys = Category.objects.all()
    sub_categorys = SubCategory.objects.all()
    
    context = {
        'categorys':categorys,
        'sub_categorys':sub_categorys,
        'message':message
    }
        
    return render(request, 'admin/Sub_Category.html', context)
    

def sub_category_edit(request, id):
    message = "";
    
    # get the sub_category to edit
    subcategory = SubCategory.objects.get(id=id)
    
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        subcategory_name = request.POST.get('sub_category')
    
        # update values
        subcategory.category_id = category_id
        subcategory.subcategory_name = subcategory_name
        subcategory.save()
        
        message = "Subcategory updated successfully"
        
    # load districts for dropdown
    categorys = Category.objects.all()
    subcategorys = SubCategory.objects.all()
        
    context = {
        'subcategory':subcategory,
        'categorys':categorys,
        'subcategorys':subcategorys,
        'message': message
    }
        
    return render(request, 'admin/Sub_Category.html', context)
    

def sub_category_delete(request, id):
    message = ""
    
    # get the subcategory
    subcategory = SubCategory.objects.get(id=id)
    
    # delete the subcategory
    subcategory.delete()
    message = "Subcategory deleted successfully"
    
    # reload data
    categorys = Category.objects.all()
    subcategorys = SubCategory.objects.all()
    
    context ={
        'categorys':categorys,
        'subcategorys':subcategorys,
        'message': message
    }
    return render(request, 'admin/Sub_Category.html', context)



def my_complaint(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'admin/My_Complaint.html', {'complaints': complaints})

def reply(request, id):
    message = ""
    complaint = Complaint.objects.get(id=id)
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        complaint.reply = reply_text
        complaint.status = 'Replied'
        complaint.save()
        message = "Replied successfully"
        
    return render(request, 'admin/Reply_Complaint.html', {'complaint': complaint, 'message':message})
    

def my_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin/My_Feedback.html', {'feedbacks': feedbacks})


def vendor_analytics(request):
    qs = (
        OrderItem.objects
        .values('product__seller__seller_name')
        .annotate(
            total_units=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('price'))
        )
        .order_by('-total_sales')
    )

    vendors = []
    sales = []
    units = []

    for row in qs:
        vendors.append(row['product__seller__seller_name'])
        sales.append(float(row['total_sales']))
        units.append(row['total_units'])

    context = {
        'vendors': json.dumps(vendors),
        'sales': json.dumps(sales),
        'units': json.dumps(units),
    }

    return render(request, 'admin/vendor_analytics.html', context)



def sales_history(request):
    qs = (
        OrderItem.objects
        .filter(order__created_at__isnull=False)
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(
            total_units=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('price'))
        )
        .order_by('month')
    )

    months, sales, units = [], [], []

    for row in qs:
        if row['month']:
            months.append(row['month'].strftime('%b %Y'))
            sales.append(float(row['total_sales']))
            units.append(row['total_units'])

    context = {
        'months': json.dumps(months),
        'sales': json.dumps(sales),
        'units': json.dumps(units),
        'history': qs,
        'has_data': bool(months),
    }

    return render(request, 'admin/sales_history.html', context)


def product_sales_distribution(request):
    qs = (
        OrderItem.objects
        .values('product__product_name')
        .annotate(
            total_sales=Sum(F('quantity') * F('price'))
        )
        .order_by('-total_sales')
    )

    products = []
    sales = []

    for row in qs:
        products.append(row['product__product_name'])
        sales.append(float(row['total_sales']))

    context = {
        'products': json.dumps(products),
        'sales': json.dumps(sales),
        'has_data': bool(products),
        'table_data': qs,
    }

    return render(request, 'admin/product_sales_distribution.html', context)




def sales_forecasting(request):
    return render(request, 'admin/sales_forecasting.html')


def logout(request):
    del request.session['aid']
    return redirect("guest:index")
    
        
        
    

        
