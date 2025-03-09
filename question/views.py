from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET, require_safe
from .models import Problem
from .forms import QuestionForm

@require_http_methods(["GET", "POST"])
def submit_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = QuestionForm()
    return render(request, 'submit_question.html', {'form': form})

@require_safe
def success(request):
    return render(request, 'success.html')

@require_POST
def remove_question(request, question_id):
    problem = get_object_or_404(Problem, id=question_id)
    problem.delete()
    return redirect('remove_success')

@require_safe
def remove_success(request):
    return HttpResponse("The question has been successfully removed!")