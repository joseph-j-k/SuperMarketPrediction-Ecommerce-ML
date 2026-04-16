from django.db import models
from administrator.models import SubCategory
from Guest.models import Seller
# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    description = models.CharField(max_length=100)
    product_image = models.ImageField(upload_to='product/product_photo/', null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    def __str__(self):
        return self.product_name
    

# class Feedback(models.Model):
#     seller = models.ForeignKey(Seller,on_delete=models.CASCADE,related_name='feedback')
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
    
    

# class Complaint(models.Model):
#     seller = models.ForeignKey(Seller,on_delete=models.CASCADE,related_name='complaints')
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#     reply = models.TextField(null=True,blank=True)
#     status = models.CharField(max_length=20,default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


class SellerSalesData(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sales_date = models.DateField()
    units_sold = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('seller', 'product', 'sales_date')
        ordering = ['sales_date']

    def __str__(self):
        return f"{self.seller} - {self.product} - {self.sales_date}"