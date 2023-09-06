from django import forms


class AsinForm(forms.Form):
    asin = forms.CharField(widget=forms.Textarea, required=True)
    path = forms.CharField(max_length=255, required=True)
