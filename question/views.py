from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Problem
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

def remove_question(request, question_id):
    """Remove a question based on its ID."""
    problem = get_object_or_404(Problem, id=question_id)
    problem.delete()
    return redirect('remove_success')  # Redirect to the new remove success page

def remove_success(request):
    """Notify the user that the question has been successfully removed."""
    return HttpResponse("The question has been successfully removed!")
