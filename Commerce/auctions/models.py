from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):

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
    image = models.URLField(blank=False) # optional
    category = models.CharField(max_length=20, choices=CATEGORIES, blank=True) # optional
    is_active = models.BooleanField(default=True, null=False) # cannot be null in database
    watchers = models.ManyToManyField(User, blank=True, related_name='watchlist')
    owner = models.ForeignKey(User, blank=False, related_name="listings", on_delete=models.CASCADE, null=True) # rmb to change null later
   
    def __str__(self):
        return f"{self.title} - {self.starting_bid}"

    def add_to_watchlist(self, user):
        self.watchers.add(user)

    def remove_from_watchlist(self, user):
        self.watchers.remove(user)


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    # bids table has a foreign key pointing to each listing
    # 1 listing can have many bids, 1 bid only points to 1 listing
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False)
    bidder = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="bids")
    # 1 user can have many bids, 1 bid only points to 1 user

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(blank=True)
    commenter = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="comments")