from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("all", views.all, name="all"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("watchlist", views.show_watchlist, name="watchlist"),
    path("categories", views.show_categories, name="categories"),
    path("categorizedlistings/<str:category>", views.show_categorized_listings, name="categorizedlistings"),
    path("listings/<str:list_id>", views.show_listing, name="showlisting"),
    path("watchlist/add/<str:list_id>", views.add_to_watchlist, name="addtowatchlist"),
    path("watchlist/remove/<str:list_id>", views.remove_from_watchlist, name="removefromwatchlist"),
    path("addBid", views.add_bid, name="addBid"),
    path("addComment", views.add_comment, name="addComment"),
    path("closeBid", views.close_bid, name="closeBid")
]
