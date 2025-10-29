from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import re
import json

from .models import User, Post

POSTS_PER_PAGE = 10

def index_redirect(request): # empty url string redirects to page 1
    return redirect('page_index', page_number=1)

def index(request, page_number):
    all_posts = Post.objects.all().order_by('-timestamp')

    # Paginate posts
    paginator = Paginator(all_posts, POSTS_PER_PAGE)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # shows the last page if page_number is out of range
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        next_url = request.GET.get('next', '')
        return render(request, "network/login.html", {'next': next_url})

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # testing out basic email regex
        valid_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.fullmatch(valid_pattern, email):
            return render(request, "network/register.html", {
                "message": "Invalid email address."
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
@login_required
def newpost(request):
    if request.method == "POST":
        content = request.POST["content"]
        # Here you would typically save the post to the database
        if content.strip() == "":
            return render(request, "network/newpost.html", {
                "error": "Post content cannot be empty."
            })
        
        post = Post(poster=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "network/newpost.html")

def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Post not found.", status=404)

    return render(request, "network/post_detail.html", {
        "post": post
    })

@login_required
def profile(request, user_id, page_number):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)

    profile_posts = Post.objects.filter(poster=user).order_by('-timestamp')
    # Paginate posts
    paginator = Paginator(profile_posts, POSTS_PER_PAGE)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # shows the last page if page_number is out of range
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/profile.html", {
        "profile_user": user,
        "posts": posts
    })

@login_required
def follow_toggle(request, user_id):
    if request.method == "POST":
        target_user = User.objects.get(id=user_id)
        target_user.followers.add(request.user) if request.user not in target_user.followers.all() else target_user.followers.remove(request.user)
        return redirect("profile", user_id=target_user.id, page_number=1)

@login_required
def following(request, page_number):
    
    followed_users = request.user.following.all()
    followed_posts = Post.objects.filter(poster__in=followed_users).order_by('-timestamp') # double underscore -> go to poster field and find all users in followed_users

    # Paginate posts
    paginator = Paginator(followed_posts, POSTS_PER_PAGE)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # shows the last page if page_number is out of range
        posts = paginator.page(paginator.num_pages)
        
    return render(request, "network/following.html", {
        "posts": posts
    })

@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.user != post.poster:
        return JsonResponse({"error": "Unauthorized."}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        new_content = data.get("content").strip()

        if new_content == "":
            return JsonResponse({"error": "Post content cannot be empty.", "current_content": new_content}, status=400)
        post.content = new_content
        post.save()
        # Return JSON instead of redirect
        return JsonResponse({
            "message": "Post updated successfully.",
            "new_content": post.content
        })
    
@login_required
def like_toggle(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count()
    })