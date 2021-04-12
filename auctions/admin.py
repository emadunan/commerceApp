from django.contrib import admin
from .models import AuctionListing, Bid, Comment

# Register models in the Admin site.
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comment)