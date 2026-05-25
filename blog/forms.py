from django import forms

WORK_TYPE_CHOICES = [
    ('', 'Select a service...'),
    ('Home Renovation', 'Home Renovation'),
    ('Home Improvements', 'Home Improvements'),
    ('Shop Fitting', 'Shop Fitting'),
    ('Restaurant Renovation', 'Restaurant Renovation'),
    ('Gardening & Landscaping', 'Gardening & Landscaping'),
    ('Other / Not Sure', 'Other / Not Sure'),
]


class ContactForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'John',
                'id': 'firstName',
            }
        ),
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Smith',
                'id': 'lastName',
            }
        ),
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'john@email.com',
                'id': 'emailAddr',
            }
        ),
    )
    phone = forms.CharField(
        label='Phone Number',
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': '07XXX XXX XXX',
                'id': 'phone',
            }
        ),
    )
    work_type = forms.ChoiceField(
        label='Type of Work',
        required=False,
        choices=WORK_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                'id': 'workType',
            }
        ),
    )
    message = forms.CharField(
        label='Tell Us About Your Project',
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Describe your project, location, timeline and any specific requirements...',
                'id': 'message',
            }
        ),
    )
