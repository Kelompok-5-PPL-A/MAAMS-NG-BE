from django import forms
from .models import Problem

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['user_email', 'question']
    
    user_email = forms.EmailField()
    question = forms.CharField(max_length=255)