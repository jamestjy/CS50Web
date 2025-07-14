from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # calling page function in views.py, passing in url title to views.page title
    # place <str:title> links at the bottom because django reads urls top to bottom
    path("wiki/search/", views.search, name="search"),
    path("wiki/create/", views.create, name="create"),
    path("wiki/random/", views.random_page, name="random"),
    path("wiki/<str:title>/", views.page, name="entry"),
    path("wiki/<str:title>/edit/", views.edit, name="edit"),
]
