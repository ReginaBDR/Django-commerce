from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("all_listings", views.all_listings, name="all_listings"),
    path("category_sort/<str:category>", views.category_sort,
         name="category_sort"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("watchlist/<str:user_id>", views.watchlist, name="watchlist"),
    path("add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist", views.remove_watchlist, name="remove_watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("close_listing", views.close_listing, name="close_listing")
]
