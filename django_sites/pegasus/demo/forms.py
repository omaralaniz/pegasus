from django import forms
from .models import *


class SearchForm(forms.Form):
    form_residence_options = [('all', 'All')] + Domicile.residence_options
    residence_type = forms.ChoiceField(
        label="Residence type", choices=form_residence_options, required=False)
    pet_friendly = forms.BooleanField(label="Allows pets", required=False)
    bed_count = forms.IntegerField(
        label="Bedrooms", min_value=0, required=False)
    bath_count = forms.IntegerField(
        label="Bathrooms", min_value=0, required=False)
    size = forms.FloatField(
        label="Square Footage", min_value=0.0, required=False)
    price = forms.FloatField(label="Price", min_value=0.0, required=False)
    city = forms.CharField(label="City", max_length=20, required=False)
    zip_code = forms.IntegerField(label="Zip Code", required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['city'].widget.attrs['placeholder'] = 'Search By City'
        self.fields['bed_count'].widget.attrs['placeholder'] = '# Bed'
        self.fields['bath_count'].widget.attrs['placeholder'] = '# Bath'


class LoginForm(forms.Form):
    MAX_FIELD_LENGTH = 20
    username = forms.CharField(label="", max_length=MAX_FIELD_LENGTH, widget=forms.TextInput(
        attrs={
            'class': 'form-control col-auto',
            'placeholder': 'username'
        }
    ))
    password = forms.CharField(
        label="", help_text='max 20 characters', max_length=MAX_FIELD_LENGTH, widget=forms.PasswordInput(
            attrs={
                'class': 'form-control col-auto',
                'placeholder': 'password'
            }
        ))


class CompatibilityScoreForm(forms.Form):
    SCALE_CHOICES = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
    ]
    # TODO: Define all attributes/fields for compatibility score
    cleanliness = forms.ChoiceField(
        label="Cleanliness", choices=SCALE_CHOICES, widget=forms.RadioSelect)
    socialness = forms.ChoiceField(
        label="Socialness", choices=SCALE_CHOICES, widget=forms.RadioSelect)
    partyness = forms.ChoiceField(
        label="Partyness", choices=SCALE_CHOICES, widget=forms.RadioSelect)


class DeleteUserForm(forms.Form):
    comment = forms.CharField(
        label="Comments", max_length=250, widget=forms.Textarea)


class CreateDomicileForm(forms.ModelForm):
    class Meta:
        model = Domicile

        fields = (
            'residence_type', 'address', 'city', 'state', 'zip_code', 'size', 'bed_count', 'bath_count'
        )


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = ValidListing

        fields = (
            'owner', 'price', 'pet_friendly', 'pets_allowed', 'limit_tenant_count', 'current_tenant_count', 'amenities',
            'utilities_included_rent', 'is_active', 'description'
        )
        widgets = {
            'pets_allowed': forms.Textarea,
            'description': forms.Textarea
        }


class EditListingForm(forms.ModelForm):
    class Meta:
        model = ValidListing
        fields = (
            'owner', 'price',  'pet_friendly', 'pets_allowed', 'limit_tenant_count', 'current_tenant_count', 'amenities',
            'utilities_included_rent', 'is_active', 'description'
        )
        widgets = {
            'description': forms.Textarea
        }


# class CreateUserForm(forms.ModelForm):
#     confirm_password = forms.CharField(
#         label="Confirm password", max_length=20, widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = (
#             'first_name', 'last_name', 'date_of_birth', 'physical_address', 'city', 'state', 'zip_code', 'phone_number',
#             'is_student', 'email', 'username', 'password'
#         )
#         labels = {
#             'is_student': 'Are you a student? '
#         }
#         widgets = {
#             'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
#             'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
#
#             'password': forms.PasswordInput
#         }
    # first_name = forms.CharField(widget=forms.TextInput
    #                              (attrs={'placeholder': 'First name'}))
    # last_name = forms.CharField(widget=forms.TextInput
    #                             (attrs={'placeholder': 'Last Name'}))
    # email = forms.CharField(widget=forms.TextInput
    #                         (attrs={'placeholder': 'abc@def.com'}))
    # username = forms.CharField(widget=forms.TextInput
    #                            (attrs={'placeholder': 'username'}))
    # date_of_birth = forms.CharField(widget=forms.TextInput
    #                                 (attrs={'placeholder': 'Date Of Birth'}))
    # physical_address = forms.CharField(widget=forms.TextInput
    #                                    (attrs={'placeholder': 'Adress'}))
    # city = forms.CharField(widget=forms.TextInput
    #                        (attrs={'placeholder': 'city'}))
    # state = forms.CharField(widget=forms.TextInput
    #                         (attrs={'placeholder': 'state'}))
    # zip_code = forms.CharField(widget=forms.TextInput
    #                            (attrs={'placeholder': 'zip code'}))
    # phone_number = forms.CharField(widget=forms.TextInput
    #                                (attrs={'placeholder': '(888) 888 - 8888'}))
    # password = forms.CharField(widget=forms.PasswordInput
    #                            (attrs={'placeholder': 'Password'}))
    # confirm_password = forms.CharField(widget=forms.PasswordInput
    #                                    (attrs={'placeholder': 'Confirm password'}))
#
#
# class EditUserForm(forms.ModelForm):
#     class Meta:
#         model = RegisteredUser
#         fields = (
#             'first_name', 'last_name', 'date_of_birth', 'physical_address', 'city', 'state', 'zip_code', 'phone_number',
#             'bio', 'profile_picture', 'email', 'username'
#         )
#         widgets = {
#             'bio': forms.Textarea
#         }


class ForgotPasswordForm(forms.Form):
    email = forms.CharField(label="Email", max_length=20)
