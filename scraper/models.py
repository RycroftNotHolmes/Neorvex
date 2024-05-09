from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    PID = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    rating = models.FloatField()
    specifications = models.TextField()
    predicted_rating = models.FloatField(default=0.0)

class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image1 = models.ImageField()
    image2 = models.ImageField()
    image3 = models.ImageField()
    image4 = models.ImageField()

class Prices(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.CharField(max_length=255)
    price = models.FloatField()
    url = models.URLField()
    
    class Meta:
        ordering = ['price']

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)
    review = models.TextField()
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    PID = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    rating = models.FloatField()
    specifications = models.TextField()
    image1 = models.ImageField()
    image2 = models.ImageField()
    image3 = models.ImageField()
    image4 = models.ImageField()
    predicted_rating = models.FloatField(default=0.0)