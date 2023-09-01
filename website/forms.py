from django import forms


class AsinForm(forms.Form):
    asin = forms.CharField(max_length=200, required=True)
    path = forms.CharField(max_length=200, required=True)