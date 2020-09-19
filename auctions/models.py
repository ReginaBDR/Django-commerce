from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Listing",
        related_name="watchlist",
        blank=True
    )


def get_category_label(category_key):
    for key, value in Listing.CATEGORY_CHOICES:
        if key == category_key:
            return value
            

class Listing(models.Model):
    ACTIVE = "A"
    CLOSED = "C"

    APPLIANCES = "P"
    FASHION = "F"
    FURNITURE = "U"
    GENERAL = "G"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (CLOSED, "Closed")
    )
    CATEGORY_CHOICES = (
        (GENERAL, "No Category"),
        (FASHION, "Fashion"),
        (FURNITURE, "Furniture"),
        (APPLIANCES, "Appliances")
    )
    image_url = models.URLField(max_length=200, blank=True)
    headline = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listing_owner"
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES,
                                default=GENERAL)
    min_bid = models.DecimalField(
        max_digits=6, decimal_places=0, default=0,
        validators=[MinValueValidator(1,
                                      message="Bid must be greater than $0.")])
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default="A")
    listing_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.headline} ({self.owner.username})"

            
    def top_bid(self):
        try:
            amount = 0
            top_bid = None
            for bid in self.bid_listing.all():
                if int(bid.bid) > int(amount):
                    amount = bid.bid
                    top_bid = bid
            return top_bid
        except ValueError:
            return None


class Bid(models.Model):
    bid = models.DecimalField(max_digits=6, decimal_places=0, default=0)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bid_owner"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bid_listing",
        default=1
    )
    bid_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bid}"


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comment_listing"
    )
    headline = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_owner",
        default=1
    )
    comment_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['comment_date']

    def __str__(self):
        return f"{self.headline} ({self.owner.username})"
