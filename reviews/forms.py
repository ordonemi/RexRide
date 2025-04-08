from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'type': 'range',  # HTML5 range input
                'min': 1,
                'max': 5,
                'step': 1,
                'class': 'form-range',  # Bootstrap class for sliders
            }),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }