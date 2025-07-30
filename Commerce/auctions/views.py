from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listings
from django.contrib.auth.decorators import login_required


def index(request):
    # get only active listings
    listings = Listings.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings})


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
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
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
        "listing": listing
    })
