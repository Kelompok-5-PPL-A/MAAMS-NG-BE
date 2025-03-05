from django import forms
from .models import Problem

class QuestionForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingin menganalisis apa hari ini ...'
        }),
    )
    question = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pertanyaan apa yang ingin ditanyakan ...'
        }),
    )
    status = forms.ChoiceField(
        choices=Problem.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='PRIBADI',
    )

    class Meta:
        model = Problem
        fields = ['title', 'question', 'status']