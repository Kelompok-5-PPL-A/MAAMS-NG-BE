from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET, require_safe
from .models import Problem
from .forms import QuestionForm

@require_GET
def display_question_form(request):
    """Display the question submission form."""
    form = QuestionForm()
    return render(request, 'submit_question.html', {'form': form})

@require_POST
def process_question_form(request):
    """Process the submitted question form."""
    form = QuestionForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('success')
    return render(request, 'submit_question.html', {'form': form})

@require_safe  # Equivalent to @require_http_methods(["GET", "HEAD"])
def success(request):
    return render(request, 'success.html')

@require_POST  # Only allow POST method for deletion operations
def remove_question(request, question_id):
    """Remove a question based on its ID."""
    problem = get_object_or_404(Problem, id=question_id)
    problem.delete()
    return redirect('remove_success')  # Redirect to the new remove success page

@require_safe  # Equivalent to @require_http_methods(["GET", "HEAD"])
def remove_success(request):
    """Notify the user that the question has been successfully removed."""
    return HttpResponse("The question has been successfully removed!")