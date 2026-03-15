from django import forms
from .models import Booking
from django.utils import timezone


class BookingForm(forms.ModelForm):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'min': str(timezone.now().date())}))
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    guests = forms.IntegerField(
        min_value=1, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '10'}))
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Any special requests?'}))

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests', 'special_requests']

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out:
            if check_in < timezone.now().date():
                raise forms.ValidationError("Check-in date cannot be in the past.")
            if check_out <= check_in:
                raise forms.ValidationError("Check-out must be after check-in.")
            if (check_out - check_in).days > 30:
                raise forms.ValidationError("Maximum booking duration is 30 nights.")
        return cleaned
