from django.contrib.auth.models import AbstractUser
from django.db import models

from datetime import datetime

class User(AbstractUser):
    watchlist = models.ManyToManyField('auctions.AuctionListing', blank=True, related_name="followers")


class AuctionListing(models.Model):
    title = models.CharField(max_length=24)
    description = models.TextField(max_length=199)
    bidInit_val = models.FloatField()
    photoUrl = models.TextField()
    category = models.CharField(max_length=64)
    createdAt = models.DateTimeField(default=datetime.now, blank=True)
    listedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_posted")
    active_state = models.IntegerField()

    def __str__(self):
        return f"[{self.id}] title: {self.title} (createdAt: {self.createdAt})"


class Bid(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_val = models.FloatField()
    createdAt = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"[{self.id}] {self.user.username}, transacted on {self.listing.title}"


class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    createdAt = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"[{self.id}] {self.user.username}, commented on {self.listing.title}"