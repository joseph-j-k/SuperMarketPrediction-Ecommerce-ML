from django.db import models
from vendor.models import Product
from Guest.models import User, Seller
from django.utils.timezone import now
# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product', null=True, blank=True)
    quantity = models.IntegerField(default=1)
    
    def total_price(self):
        return float(self.product.price) * self.quantity

class Order(models.Model):
    order_number = models.CharField(max_length=30, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # save first to get ID

        if not self.order_number:
            date_part = now().strftime("%Y%m%d")
            self.order_number = f"ORD-{date_part}-{self.id:05d}"
            super().save(update_fields=['order_number'])

    def __str__(self):
        return self.order_number
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def item_total(self):
        return self.price * self.quantity


class Feedback(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        null=True,
        blank=True
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    

class Complaint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints',
        null=True,
        blank=True
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='complaints',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    reply = models.TextField(null=True,blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Replied', 'Replied'),
        ('Closed', 'Closed'),
    ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField()
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)