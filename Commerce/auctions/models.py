from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listings(models.Model):

    CATEGORIES = [
    ("electronics", "Electronics"),
    ("clothing", "Clothing"),
    ("home_kitchen", "Home & Kitchen"),
    ("beauty", "Beauty & Personal Care"),
    ("sports", "Sports & Outdoors"),
    ("toys", "Toys & Games"),
    ("books", "Books"),
    ("groceries", "Groceries"),
    ("furniture", "Furniture"),
    ("automotive", "Automotive"),
]

    # user needs to type at least title, desc and starting bid
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(blank=False)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10, blank=False)
    image = models.URLField(blank=True) # optional
    category = models.CharField(max_length=20, choices=CATEGORIES, blank=True) # optional
    is_active = models.BooleanField(default=True, null=False) # cannot be null in database
    watchers = models.ManyToManyField(User, blank=True, related_name='watchlist')
   
    def __str__(self):
        return f"{self.title} - {self.starting_bid}"

    def add_to_watchlist(self, user):
        self.watchers.add(user)

    def remove_from_watchlist(self, user):
        self.watchers.remove(user)


