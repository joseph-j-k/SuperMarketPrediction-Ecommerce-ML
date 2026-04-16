from django.db import models
from administrator.models import Place
# Create your models here.
class User(models.Model):
    id = models.CharField(
        max_length=7,
        primary_key=True,
        editable=False
    )
    user_name = models.CharField(max_length=100)
    user_email = models.CharField(max_length=100)
    user_password = models.CharField(max_length=100)
    user_contact = models.CharField(max_length=100)
    user_address = models.TextField()
    user_photo = models.ImageField(upload_to='user/user_photo/', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='user_guests', null=True, blank=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            last = User.objects.order_by('id').last()
            if last:
                number = int(last.id[1:]) + 1
            else:
                number = 1
            self.id = f"U{number:06d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user_name
    

class Seller(models.Model):
    id = models.CharField(
        max_length=7,
        primary_key=True,
        editable=False
    )
    
    seller_name = models.CharField(max_length=100)
    seller_email = models.CharField(max_length=100)
    seller_password = models.CharField(max_length=100)
    seller_contact = models.CharField(max_length=100)
    seller_address = models.CharField(max_length=100)
    seller_photo = models.ImageField(upload_to='seller/seller_photo/', null=True, blank=True)
    seller_proof = models.ImageField(upload_to='seller/seller_proof/', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='seller_guests', null=True, blank=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            last = Seller.objects.order_by('id').last()
            if last:
                number = int(last.id[1:]) + 1
            else:
                number = 1
            self.id = f"S{number:06d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.seller_name