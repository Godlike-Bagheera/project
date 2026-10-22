from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} ★') for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
            'text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Поделитесь своим мнением...'}
            ),
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Комментарий',
        }