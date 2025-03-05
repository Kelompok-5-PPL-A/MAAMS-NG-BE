from django.shortcuts import render, redirect
from .forms import QuestionForm

def submit_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = QuestionForm()
    return render(request, 'submit_question.html', {'form': form})

def success(request):
    return render(request, 'success.html')
