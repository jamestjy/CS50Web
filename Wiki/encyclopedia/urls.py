from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # calling page function in views.py, passing in url title to views.page title
    path("<str:title>/", views.page, name="entry"),
    path("search", views.search, name="search"), # take note DO NOT add a slash after the path
    
]
