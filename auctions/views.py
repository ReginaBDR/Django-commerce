from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from . import models
from .forms import ListingForm, CommentForm, RegisterForm, BidForm
from .models import User, Listing, Comment


def index(request):
    listings = Listing.objects.all().filter(status=Listing.ACTIVE).order_by(
        '-listing_date'
    )
    if request.user.is_authenticated:
        user_watchlist = User.objects.get(
            pk=int(request.user.id)).watchlist.all()
        return render(request, "auctions/index.html",
                      {"listings": listings,
                       "watchlist": user_watchlist})
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            login(request, user)
            messages.add_message(
                request,
                messages.SUCCESS,
                "You are now logged in.")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(
                request,
                messages.WARNING,
                "We had Login troubles. Please check your username and "
                + "password or register if you haven't already.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.add_message(
        request,
        messages.SUCCESS,
        "You've been logged out.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password'])
                user.save()
            except IntegrityError:
                messages.add_message(request, messages.WARNING,
                                     "Username already taken.")
                return render(request, "auctions/register.html")
            login(request, user)
            messages.add_message(
                request,
                messages.SUCCESS,
                "You are successfully registered")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.WARNING,
                                 "Something went wrong")
            return render(request, "auctions/register.html", {"form": form})
    else:
        return render(request, "auctions/register.html",
                      {"form": RegisterForm()})


@require_http_methods(["POST"])
def place_bid(request):
    top_bid = 0
    try:
        bid_listing = Listing.objects.get(pk=int(request.POST["listing_id"]))
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")

    if bid_listing.top_bid():
        top_bid = int(bid_listing.top_bid().bid)
    form = BidForm(request.POST,
                   min_bid=int(bid_listing.min_bid),
                   top_bid=top_bid)
    if form.is_valid():
        try:
            new_bid = form.save(commit=False)
            new_bid.listing = bid_listing
            new_bid.owner = request.user
            new_bid.save()
        except IntegrityError:
            messages.add_message(request, messages.WARNING,
                                 "Unable to place your bid.")
            return HttpResponseRedirect(
                reverse("listing", args=(bid_listing.id,)))
        messages.add_message(request, messages.SUCCESS,
                             "Your bid was successful.")
        return HttpResponseRedirect(reverse("listing", args=(bid_listing.id,)))
    messages.add_message(request, messages.WARNING,
                         "Unable to process your bid.")
    list_args = {"comment_form": None,
                 "bid_form": form,
                 "listing_id": request.POST["listing_id"],
                 "user_id": request.user.id}
    return render(request, "auctions/listing.html",
                  _get_listing_dict(list_args))


def listing(request, listing_id):
    list_args = {"comment_form": None,
                 "bid_form": None,
                 "listing_id": listing_id,
                 "user_id": request.user.id}
    return render(request, "auctions/listing.html",
                  _get_listing_dict(list_args))


def _get_listing_dict(list_args):
    comment_form = list_args["comment_form"]
    if not comment_form:
        comment_form = CommentForm()

    bid_form = list_args["bid_form"]
    if not bid_form:
        bid_form = BidForm()

    listing_id = list_args["listing_id"]
    user_id = list_args["user_id"]
    user_watchlist = None

    try:
        view_listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.get_queryset().filter(listing=view_listing)
        if user_id:
            user_watchlist = User.objects.get(pk=int(user_id)).watchlist.all()
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    except User.DoesNotExist:
        raise Http404("User not found.")
    return {
        "listing": view_listing,
        "form": bid_form,
        "comment_form": comment_form,
        "comments": comments,
        "watchlist": user_watchlist
    }


def all_listings(request):
    listings = Listing.objects.all().order_by('-listing_date')
    user_watchlist = None
    if request.user.is_authenticated:
        user_watchlist = User.objects.get(
            pk=int(request.user.id)).watchlist.all()
    return render(request, "auctions/all_listings.html", {
        "listings": listings,
        "category": Listing.CATEGORY_CHOICES,
        "watchlist": user_watchlist,
        "category_heading": "All Listings"
    })


def category_sort(request, category):
    if category == "N":
        listings = Listing.objects.all().filter(
            owner=request.user.id).order_by('-listing_date')
        heading = "Listings"
    else:
        listings = Listing.objects.all().filter(
            category=category, status=Listing.ACTIVE).order_by('-listing_date')
        heading = models.get_category_label(category)

    return render(request, "auctions/all_listings.html", {
        "listings": listings,
        "category": Listing.CATEGORY_CHOICES,
        "category_heading": heading
    })


@require_http_methods(["POST"])
@login_required(login_url="/login")
def close_listing(request):
    try:
        target_listing = Listing.objects.get(
            pk=int(request.POST["listing_id"]))
        target_listing.status = Listing.CLOSED
        target_listing.save()
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    messages.add_message(request, messages.SUCCESS,
                         "Auction has been closed.")
    return HttpResponseRedirect(
        reverse("listing", args=(request.POST["listing_id"],)))


@login_required(login_url="/login")
def create_listing(request):
    form = ListingForm(request.POST)
    form.owner = request.user
    if request.method == "POST":
        if form.is_valid():
            try:
                new_listing = form.save(commit=False)
                new_listing.owner = request.user
                new_listing.save()
            except IntegrityError:
                messages.add_message(request, messages.WARNING,
                                     "Unable to add the listing.")
                return render(request, "auctions/create_listing.html",
                              {"form": form})
            messages.add_message(request, messages.SUCCESS,
                                 "Your listing has been created.")
            return HttpResponseRedirect(
                reverse("listing", args=(new_listing.id,)))
        messages.add_message(request, messages.WARNING,
                             "Something went wrong. Please try again.")
        return render(request, "auctions/create_listing.html", {"form": form})
    else:
        return render(request, "auctions/create_listing.html",
                      {"form": ListingForm()})


@require_http_methods(["POST"])
@login_required(login_url="/login")
def add_comment(request):
    form = CommentForm(request.POST)
    if form.is_valid():
        try:
            target_listing = Listing.objects.get(
                pk=int(request.POST["listing_id"]))
            new_comment = form.save(commit=False)
            new_comment.listing = target_listing
            new_comment.owner = request.user
            new_comment.save()
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")
        except IntegrityError:
            messages.add_message(
                request,
                messages.WARNING,
                "Unable to add the comment. "
                + "Please give it another try"
            )
            return HttpResponseRedirect(
                reverse("listing", args=(target_listing.id,)))
        messages.add_message(request, messages.SUCCESS,
                             "Your comment has been saved")
        return HttpResponseRedirect(
            reverse("listing", args=(target_listing.id,)))
    messages.add_message(request, messages.WARNING,
                         "Unable to add the comment.")
    messages.add_message(request, messages.WARNING,
                         _process_form_errors(form))
    list_args = {"comment_form": form,
                 "bid_form": None,
                 "listing_id": request.POST["listing_id"],
                 "user_id": request.user.id}
    return render(request, "auctions/listing.html",
                  _get_listing_dict(list_args))


def _process_form_errors(form):
    error_message = ""
    for field, validation_error in form.errors.as_data().items():
        error_message = error_message + field.title() + ": "
        for warning in validation_error:
            for item in warning:
                error_message = error_message + " " + item + " "
    return error_message


@login_required(login_url="/login")
def watchlist(request, user_id):
    try:
        user_watchlist = User.objects.get(pk=int(user_id)).watchlist.all()
    except User.DoesNotExist:
        raise Http404("User not found.")
    return render(request, "auctions/all_listings.html", {
        "listings": user_watchlist,
        "category": Listing.CATEGORY_CHOICES,
        "watchlist_flag": "True",
        "category_heading": "Watchlist"
    })


@login_required(login_url="/login")
def add_watchlist(request):
    try:
        user = User.objects.get(pk=int(request.user.id))
        selected_listing = Listing.objects.get(
            pk=int(request.POST["listing_id"])
        )
        user.watchlist.add(selected_listing)
    except User.DoesNotExist:
        raise Http404("User not found.")
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    except IntegrityError:
        return render(request, "auctions/index.html", {
            "message": "Failed when adding to watchlist.",
            "watchlist_flag": "True"
        })
    messages.add_message(request, messages.SUCCESS,
                         "The listing has been added. ")
    return HttpResponseRedirect(reverse("watchlist", args=(user.id,)))


@require_http_methods(["POST"])
@login_required(login_url="/login")
def remove_watchlist(request):
    try:
        delete_listing = Listing.objects.get(
            pk=int(request.POST["listing_id"]))
        user = User.objects.get(pk=int(request.user.id))
        user.watchlist.remove(delete_listing)
    except User.DoesNotExist:
        raise Http404("User not found.")
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    except IntegrityError:
        messages.add_message(request, messages.WARNING,
                             "Failed to remove this item from Watchlist. "
                             + "Please try again.")
        return HttpResponseRedirect(
            reverse("listing", args=(delete_listing.id,)))
    messages.add_message(request, messages.SUCCESS,
                         "This listing has been removed from your "
                         + "Watchlist.")
    return HttpResponseRedirect(reverse("listing", args=(delete_listing.id,)))