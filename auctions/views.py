from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Bid, Comment
from django import forms
from datetime import datetime
from django.db.models import Max, Count, Q
from django.contrib.auth.decorators import login_required

# CONSTANTS
CATEGORIES = [(None, "not categorized"), ("fashion", "fashion"), ("toys", "toys"), ("electronics", "electronics"), ("home", "home")]

# FORMS:

class NewListingForm(forms.Form):
    title = forms.CharField(label="title", max_length=24)
    category = forms.MultipleChoiceField(required=False, widget=forms.Select, choices=CATEGORIES)
    bidInit_val = forms.FloatField()
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), max_length=199)
    photoUrl = forms.URLField(required=False)

# VIEWS:
def index(request):
    auctionListings = AuctionListing.objects.all()

    for auctionListing in auctionListings:
        maxPrice = Bid.objects.filter(listing=auctionListing).aggregate(Max('bid_val'))
        auctionListing.maxPrice = (maxPrice['bid_val__max'])

    return render(request, "auctions/index.html", {
        "auctionListings": auctionListings
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)

        if form.is_valid:
            curr_user = User.objects.get(pk=request.user.id)
            newlist = AuctionListing(
                title = request.POST["title"],
                description = request.POST["description"],
                bidInit_val = float(request.POST["bidInit_val"]),
                photoUrl = request.POST["photoUrl"],
                category = request.POST["category"],
                active_state = 1,
                listedBy = curr_user
                )
            newlist.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })

    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

@login_required
def show_listing(request, list_id):
    curr_user = User.objects.get(pk=request.user.id)
    listing = AuctionListing.objects.get(pk=list_id)

    if listing in curr_user.watchlist.all():
        listedInWatchlist = True
    else:
        listedInWatchlist = False

    comments = Comment.objects.filter(listing=listing).order_by('createdAt').reverse()

    # Get the max price for this auction listing
    maxbid = Bid.objects.filter(listing=listing).aggregate(Max('bid_val'))
    
    maxbid_val = maxbid['bid_val__max'] #if maxbid['bid_val__max'] != None else 0
    
    # Get the Winner
    maxBid_obj = Bid.objects.filter(listing=listing, bid_val=maxbid_val)

    if maxBid_obj:
        maxBid_obj = Bid.objects.get(listing=listing, bid_val=maxbid_val)
        winner = maxBid_obj.user.username
    else:
        winner = "no one"

    # Count bid(s)
    counter = 0
    listing_bids = Bid.objects.filter(listing=listing)
    for bid in listing_bids:
        counter += 1

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "listedInWatchlist": listedInWatchlist,
        "comments": comments,
        "max_price": maxbid_val,
        "winner":  winner,
        "bids_count": counter
    })

@login_required
def show_categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIES
    })


@login_required
def show_categorized_listings(request, category):
    listings = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/categorized.html", {
        "listings": listings,
        "category": category
    })


@login_required
def show_watchlist(request):
    curr_user = User.objects.get(pk=request.user.id)
    watchlist = curr_user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


@login_required
def add_to_watchlist(request, list_id):
    curr_user = User.objects.get(pk=request.user.id)
    listing = AuctionListing.objects.get(pk=list_id)

    curr_user.watchlist.add(listing)
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def remove_from_watchlist(request, list_id):
    curr_user = User.objects.get(pk=request.user.id)
    listing = AuctionListing.objects.get(pk=list_id)

    if listing:
        curr_user.watchlist.remove(listing)
    else:
        return render(request, "auctions/error.html", {
            "message": "Listing cannot be removed"
        })

    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def add_bid(request):
    if request.method == "POST":
        bid_val = request.POST["bid_val"]
        listing_id = request.POST["listing_id"]

        if not bid_val:
            return render(request, "auctions/error.html", {
                "message": "Your bid must be greater than any other bids that have been placed!"
            })

        auctionListing = AuctionListing.objects.get(pk=listing_id)
        curr_user = User.objects.get(pk=request.user.id)

        maxbid = Bid.objects.filter(listing=auctionListing).aggregate(Max('bid_val'))

        if maxbid["bid_val__max"]:
            if maxbid['bid_val__max'] >= float(bid_val):
                return render(request, "auctions/error.html", {
                    "message": "Your bid must be greater than any other bids that have been placed!"
                })
        else:
            if auctionListing.bidInit_val > float(bid_val):
                return render(request, "auctions/error.html", {
                    "message": "Your bid must be at least as large as the starting bid!"
                })

        bid = Bid(
            listing = auctionListing,
            user = curr_user,
            bid_val = float(bid_val)
        )

        bid.save()
        return HttpResponseRedirect(reverse("showlisting", args=(listing_id,)))


@login_required
def add_comment(request):
    if request.method == "POST":
        content = request.POST["content"]
        listing_id = request.POST["listing_id"]

        auctionListing = AuctionListing.objects.get(pk=listing_id)
        curr_user = User.objects.get(pk=request.user.id)

        comment = Comment(
            listing = auctionListing,
            user = curr_user,
            content = content
        )

        comment.save()
        return HttpResponseRedirect(reverse("showlisting", args=(listing_id,)))


@login_required
def close_bid(request):
    listing_id = request.POST["listing_id"]

    auctionListing = AuctionListing.objects.get(pk=listing_id)
    curr_user = User.objects.get(pk=request.user.id)

    if curr_user.username == auctionListing.listedBy.username:
        auctionListing.active_state = 0
        auctionListing.save()
        return HttpResponseRedirect(reverse("showlisting", args=(listing_id,)))