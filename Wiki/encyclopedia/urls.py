from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # calling page function in views.py, passing in url title to views.page title
    path("wiki/search/", views.search, name="search"),
    path("wiki/create/", views.create, name="create"),
    path("wiki/random/", views.random, name="random"),
    path("wiki/<str:title>/", views.page, name="entry"),
    path("wiki/<str:title>/edit/", views.edit, name="edit"),
]
