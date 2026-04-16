from django.db import models

# Create your models here.
class Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.CharField(max_length=100)
    admin_password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.admin_name
    
class District(models.Model):
    district_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.district_name
    

class Place(models.Model):
    place_name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.place_name
    

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.category_name
    
    
class SubCategory(models.Model):
    subcategory_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.subcategory_name
    

    
        
    
    

    