from django.contrib import admin
from auctions.models import User, Listing, Comment, Bid


class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)


class BidAdmin(admin.ModelAdmin):
    list_display = ("bid", "listing", "owner", "bid_date")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("owner", "headline", "listing", "comment_date")


class ListingAdmin(admin.ModelAdmin):
    list_display = ("headline", "owner", "category", "status", "listing_date")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
