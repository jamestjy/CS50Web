from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from .models import User, Listings, Bids
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation


def index(request):
    # get only active listings
    listings = Listings.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "user": request.user})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        # if user already exists, IntegrityError will be raised
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        # reverse is used to get URL using its name, instead of hardcoding
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def create_listing(request):
    categories = Listings.CATEGORIES
    if request.method == "POST":
        title = request.POST.get["title"]
        description = request.POST.get["description"]
        starting_bid = Decimal(request.POST.get["starting_bid"])
        image = request.POST.get("image", "")
        category = request.POST.get("category", "")

        # validate that required fields are filled
        if not title or not description or not starting_bid:
            return render(request, "auctions/create_listing.html", {
                "message": "Title, description, and starting bid are required.",
                "categories": categories
            })
        
        # Create a new listing
        listing = Listings(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image=image,
            category=category
        )

        listing.save()
        # redirect user to the newly created listing page
        return redirect("listing", listing_id=listing.id)
    
    return render(request, "auctions/create_listing.html", {
        "categories": categories})

def listing(request, listing_id):
    try:
        listing = Listings.objects.get(id=listing_id)
    except Listings.DoesNotExist:
        # if listing does not exist, return a 404 error
        return render(request, "auctions/404.html", {"error_message": "Listing does not exist"}, 
                      status=404)
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user": request.user  # can just get user this way in django directly
    })


@login_required
def add_to_watchlist(request, listing_id):
    listing = Listings.objects.get(id=listing_id)
    listing.add_to_watchlist(request.user)
    return redirect("listing", listing_id=listing.id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listings.objects.get(id=listing_id)
    listing.remove_from_watchlist(request.user)
    return redirect("listing", listing_id=listing.id)

@login_required
def show_watchlist(request):
    watched_items = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"watched_items": watched_items,
                                                       "user": request.user})

def show_categories(request):
    # can only show existing categories
    used_categories = Listings.objects.values_list('category', flat=True).distinct()
    category_map = dict(Listings.CATEGORIES) # must pass as human-readable label instead of what is stored in database

    categories_with_labels = [(key, category_map[key]) for key in used_categories]

    return render(request, "auctions/categories.html", {"categories": categories_with_labels})

def show_category_listings(request, category):
    listings = list(Listings.objects.filter(category=category)) # dont use .get() since get expects only 1 object returned
    # remember the variable "category" is currently the human readable label, must convert
    # list() is used to convery QuerySet into a list

    if not listings: # if no listings under such category
        return render(request, "auctions/404.html", {"error_message": f"No listings under {category}"})
    
    return render(request, "auctions/category_listings.html", {"listings": listings, 
                                                             "category": category})

@login_required
def bid(request, listing_id):

    listing = Listings.objects.get(id=listing_id)
    if request.method == "POST":
        try:
            bid_amount = Decimal(request.POST.get("bid_amount"))
        except (InvalidOperation, TypeError):
            # if bid format is invalid
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "user": request.user,
                "error_message": "Invalid bid amount"
                })
            

        # get current highest bid
        highest_bid = listing.starting_bid

        if bid_amount > highest_bid:
            # set new price
            listing.starting_bid = bid_amount
            listing.save()
            # create new bid instance
            Bids.objects.create(
                listing = listing,
                amount = bid_amount,
                bidder = request.user
            )
            messages.success(request, "Bid placed successfully")

        else:
            messages.error(request, "Bid amount must be higher than current price")
            
        return redirect('listing', listing_id=listing.id)


        
        


        


