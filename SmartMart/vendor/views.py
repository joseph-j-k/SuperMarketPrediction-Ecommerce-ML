from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd

from Guest.models import Seller
from .models import Product
from administrator.models import Category, SubCategory
from User.models import Order, OrderItem, Complaint, Feedback
from .ml_utils import baseline_forecast
from .utils import load_historical_sales_from_db, prepare_historical_summary
from .ml.forecast import forecast_seller_products
from .analytics.data_loader import load_seller_product_sales
from .analytics.summary import monthly_product_sales

# Create your views here.
def vendor_home(request):
    return render(request, 'vendor/Vendor_Home.html')

def profile(request):
    vendor = Seller.objects.get(id=request.session['sid'])
    return render(request, 'vendor/My_Profile.html', {'vendor':vendor})

def edit_profile(request):
    vendor = Seller.objects.get(id=request.session['sid'])
    message = ""
    if request.method == 'POST':
        vendor.seller_name = request.POST.get('full_name')
        vendor.seller_email = request.POST.get('email')
        vendor.seller_contact = request.POST.get('contact')
        vendor.seller_address = request.POST.get('address')
        if request.FILES.get('photo'):
            vendor.seller_photo = request.FILES.get('photo')
        vendor.save()
        message = "Profile updated successfully!"
    
    context = {
        'vendor':vendor,
        "message": message
    }
        
    return render(request, 'Vendor/Edit_Profile.html', context)

def change_password(request):
    vendor = Seller.objects.get(id=request.session['sid'])
    message=""
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        
        if old == vendor.seller_password:
            if new == confirm:
                vendor.seller_password = new
                vendor.save()
                message = "Password updated successfully!"
            else:
                message = "New password does not match"
        else:
            message = "Old password incorrect"
    
    vendor = {
        "vendor":vendor,
        "message": message
    }    
               
    return render(request, 'Vendor/Change_Password.html', vendor)


def ajax_subcategory(request):
    sub_category = SubCategory.objects.filter(category=request.GET.get('did'))
    return render(request, 'Vendor/AjaxSubCategory.html', {'sub_category':sub_category})


def product(request):
    message = ""
    sid = request.session.get('sid')
    
    if not sid:
        return redirect('guest:login')
    
    seller = Seller.objects.get(id=sid)
    category = Category.objects.all()
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        product_image = request.FILES.get('product_image')
        sub_category = request.POST.get('subcategory_id')
        
        subcategory_obj = SubCategory.objects.get(id=sub_category)
        
        Product.objects.create(
            product_name = product_name,
            price = price,
            stock = stock,
            description = description,
            product_image = product_image,
            sub_category = subcategory_obj,
            seller = seller
        )
        message = "Product saved successfully"
        
    context = {
        'category':category,
        'message':message
    }
        
        
    return render(request, 'Vendor/Add_Product.html', context)

def product_list(request):
    sid = request.session.get('sid')

    if not sid:
        return redirect('guest:login')
    
    seller = Seller.objects.get(id=sid)
    products = Product.objects.filter(seller=seller)
    return render(request, 'vendor/Product_List.html', {'products':products})

def delete_product(request, id):
    sid = request.session.get('sid')
    message = ""

    if not sid:
        return redirect('guest:login')
    
    seller = Seller.objects.get(id=sid)
    product = Product.objects.get(id=id, seller=seller)
    product.delete()
    
    products = Product.objects.all()
    message = "Product deleted successfully"
    context = {
        'products':products,
        'message':message
    }
    return render(request, 'Vendor/Product_List.html', context)


def order_list(request):
    sid = request.session.get('sid')

    if not sid:
        return redirect('guest:login')
    
    seller = Seller.objects.get(id=sid)
    orders = Order.objects.filter(
        items__product__seller=seller
    ).distinct().order_by('-created_at')
    
    return render(request, 'Vendor/OrderList.html', {
        'orders': orders
    })
    

def order_detail(request, order_id):
    sid = request.session.get('sid')

    if not sid:
        return redirect('guest:login')

    seller = Seller.objects.get(id=sid)

    # get order (only if it belongs to this user)
    order = get_object_or_404(Order, id=order_id, items__product__seller=seller)

    # get items using related_name="items"
    items = OrderItem.objects.filter(
        order=order,
        product__seller=seller
    )

    return render(request, 'Vendor/OrderDetail.html', {
        'order': order,
        'items': items
    })
    

def add_feedback(request):
    sid = request.session.get('sid')
    if not sid:
        return redirect('guest:login')
    
    message = ""
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        Feedback.objects.create(
            seller_id=sid,
            title=title,
            content=content
        )
        message = "Feedback saved successfully"
    
    feedbacks = Feedback.objects.filter(seller_id=sid).order_by('-created_at')
    context = {
        'feedbacks':feedbacks,
        'message':message
    }
    return render(request, 'Vendor/Feedback.html', context)


def add_complaint(request):
    
    sid = request.session.get('sid')
    if not sid:
        return redirect('guest:login')
    
    message = ""
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        Complaint.objects.create(
            title = title,
            content = content,
            seller_id=sid,
            status = 'Completed'
        )
        message = "Complaint saved successfully"
    complaints = Complaint.objects.filter(seller_id=sid).order_by('-created_at')
    context = {
        'complaints':complaints,
        'message':message
    }
    return render(request, 'Vendor/Complaint.html', context)


def vendor_sales_history(request):
    seller_id = request.session.get('sid')

    df = load_historical_sales_from_db()

    if df.empty:
        return render(request, 'Vendor/historical_sales.html', {
            'sales': [],
            'figures': {}
        })

    # 🔒 Filter seller
    df = df[df['seller_id'] == seller_id]

    # FIGURES
    total_sold_units = int(df['sold_units'].sum())
    total_unsold_units = int(df['unsold_units'].sum())
    total_stock = int(df['stock'].sum())
    total_revenue = float(df['revenue'].sum())

    sell_through = round(
        (total_sold_units / total_stock) * 100, 2
    ) if total_stock > 0 else 0

    figures = {
        'total_sold_units': total_sold_units,
        'total_unsold_units': total_unsold_units,
        'total_stock': total_stock,
        'total_revenue': total_revenue,
        'sell_through': sell_through
    }

    return render(request, 'Vendor/historical_sales.html', {
        'sales': df.to_dict('records'),
        'figures': figures
    })


    
    
def vendor_sales_forecast(request):
    seller_id = request.session.get("sid")

    df = load_seller_product_sales(seller_id)
    print("SELLER ID:", seller_id)
    print("RAW DF:")
    print(df.head())
    print("RAW DF SHAPE:", df.shape)

    if df.empty:
        return render(request, "Vendor/sales_forecast.html", {
            "forecast": []
        })

    monthly_df = monthly_product_sales(df)
    print("MONTHLY DF:")
    print(monthly_df.head())
    print("MONTHLY DF SHAPE:", monthly_df.shape)

    forecast_df = forecast_seller_products(monthly_df)
    print("FORECAST DF:")
    print(forecast_df)

    return render(request, "Vendor/sales_forecast.html", {
        "forecast": forecast_df.to_dict("records")
    })



def monthly_product_sales(df):
    df = df.copy()

    # datetime
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])

    # numeric safety
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # optional columns
    if "discount" not in df.columns:
        df["discount"] = 0
    if "profit" not in df.columns:
        df["profit"] = 0
    if "seller_id" not in df.columns:
        df["seller_id"] = 0

    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0)
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce").fillna(0)

    # derived fields
    df["revenue"] = df["quantity"] * df["price"]
    df["year"] = df["created_at"].dt.year
    df["month"] = df["created_at"].dt.month
    df["quarter"] = ((df["month"] - 1) // 3) + 1

    # monthly aggregation
    monthly_df = (
        df.groupby(
            ["seller_id", "product_id", "product_name", "year", "month", "quarter"],
            as_index=False
        )
        .agg(
            sold_units=("quantity", "sum"),
            revenue=("revenue", "sum"),
            avg_price=("price", "mean"),
            avg_discount=("discount", "mean"),
            total_profit=("profit", "sum"),
        )
        .sort_values(["seller_id", "product_id", "year", "month"])
        .reset_index(drop=True)
    )

    # lag features
    monthly_df["previous_month_units"] = (
        monthly_df.groupby(["seller_id", "product_id"])["sold_units"].shift(1)
    )

    monthly_df["previous_2_month_avg"] = (
        monthly_df.groupby(["seller_id", "product_id"])["sold_units"]
        .transform(lambda x: x.shift(1).rolling(2).mean())
    )

    monthly_df["previous_3_month_avg"] = (
        monthly_df.groupby(["seller_id", "product_id"])["sold_units"]
        .transform(lambda x: x.shift(1).rolling(3).mean())
    )

    monthly_df["previous_month_revenue"] = (
        monthly_df.groupby(["seller_id", "product_id"])["revenue"].shift(1)
    )

    monthly_df["previous_month_profit"] = (
        monthly_df.groupby(["seller_id", "product_id"])["total_profit"].shift(1)
    )

    # fill null lag values
    monthly_df["previous_month_units"] = monthly_df["previous_month_units"].fillna(0)
    monthly_df["previous_2_month_avg"] = monthly_df["previous_2_month_avg"].fillna(0)
    monthly_df["previous_3_month_avg"] = monthly_df["previous_3_month_avg"].fillna(0)
    monthly_df["previous_month_revenue"] = monthly_df["previous_month_revenue"].fillna(0)
    monthly_df["previous_month_profit"] = monthly_df["previous_month_profit"].fillna(0)

    return monthly_df




def logout(request):
    del request.session['sid']
    return redirect("guest:index")
    
    


