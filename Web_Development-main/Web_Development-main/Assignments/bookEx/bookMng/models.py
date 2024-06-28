from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


class MainMenu(models.Model):
    item = models.CharField(max_length=200, unique=True)
    link = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.item


class Book(models.Model):
    name = models.CharField(max_length=200)
    web = models.URLField(max_length=300)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    publishdate = models.DateField(auto_now=True)
    picture = models.FileField(upload_to='bookEx/static/uploads')
    pic_path = models.CharField(max_length=300, editable=False, blank=True)
    username = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class BookRating(models.Model):
    book_id = models.ForeignKey(Book, blank=False, null=False, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    user_id = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class Favorite(models.Model):
    book_id = models.ForeignKey(Book, blank=False, null=False, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    user_id = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class CartItem(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} of {self.book.name}"

