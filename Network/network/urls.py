
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_redirect, name="index"),
    path("page/<int:page_number>/", views.index, name="page_index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("newpost/", views.newpost, name="newpost"),
    path("profile/<int:user_id>/page/<int:page_number>/", views.profile, name="profile"),
    path("follow_toggle/<int:user_id>/", views.follow_toggle, name="follow_toggle"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("following/page/<int:page_number>/", views.following, name="following"),
    path("edit/<int:post_id>/", views.edit_post, name="edit"),
    path("like_toggle/<int:post_id>/", views.like_toggle, name="like_toggle"),
]
