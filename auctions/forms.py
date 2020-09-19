from django import forms
from django.forms import ModelForm, TextInput, PasswordInput, Textarea, \
    Select, NumberInput

from .models import Listing, Comment, Bid, User


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['headline', 'description']
        widgets = {
            'headline': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Headline'
            }),
            'description': Textarea(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Your comments'
            })
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']
        widgets = {
            'bid': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Bid here.'}
            )
        }

    def __init__(self, *args, **kwargs):
        if kwargs:
            self.top_bid = kwargs.pop('top_bid')
            self.min_bid = kwargs.pop('min_bid')
        super(BidForm, self).__init__(*args, **kwargs)

    def clean_bid(self):
        new_bid = int(self.cleaned_data['bid'])
        top_bid = int(self.top_bid)
        min_bid = int(self.min_bid)
        if new_bid == 0:
            raise forms.ValidationError(
                f"Bid cannot be $0."
            )
        if new_bid < top_bid or new_bid == top_bid:
            raise forms.ValidationError(
                "Bid has to be greater than the Current price.")

        if new_bid < min_bid:
            raise forms.ValidationError(
                "Bid has to be greater than or equal to the Starting price."
            )
        return new_bid


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['image_url', 'headline', 'description', 'category',
                  'min_bid']
        widgets = {
            'image_url': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Image url'}
            ),
            'headline': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Headline (required)'}
            ),
            'description': Textarea(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Description (required)'}
            ),
            'category': Select(choices=Listing.CATEGORY_CHOICES, attrs={
                'class': 'form-control'}),
            'min_bid': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum Bid (required)'}
            )
        }
        labels = {'image_url': '', 'headline': '', 'description': '',
                  'min_bid': 'Minimum Bid', 'category': ''}
        help_texts = {'headline': '', 'description': '', 'min_bid': ''}


class RegisterForm(ModelForm):
    confirm_password = forms.CharField(
        label='',
        help_text='',
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Confirm Password'}
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Username'}
            ),
            'email': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Email'}
            ),
            'password': PasswordInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Password'}
            ),
        }
        labels = {'username': '', 'email': '', 'password': ''}
        help_texts = {'username': '', 'password': ''}

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "The passwords entered do not match."
            )
