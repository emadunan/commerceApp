from django.contrib.auth.models import AbstractUser
from django.db import models

from datetime import datetime

class User(AbstractUser):
    watchlist = models.ManyToManyField('auctions.AuctionListing', blank=True, related_name="followers")


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    bidInit_val = models.FloatField()
    photoUrl = models.TextField()
    category = models.CharField(max_length=64)
    createdAt = models.DateTimeField(default=datetime.now, blank=True)
    listedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_posted")
    active_state = models.IntegerField()

    def __str__(self):
        return f"title: {self.title} (createdAt: {self.createdAt})"
