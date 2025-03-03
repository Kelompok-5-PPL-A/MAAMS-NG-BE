from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import IntegrityError
from .models import Problem
from .forms import QuestionForm

def submit_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            try:
                # Get or create the user (in a real app, this would likely come from the session)
                user_email = form.cleaned_data['user_email']
                
                # Create the problem (question)
                question = form.cleaned_data['question']
                new_problem = Problem.objects.create(
                    user_email=user_email,
                    question=question,
                )

                # If the problem is saved successfully, redirect to success page
                return redirect('success')
            except IntegrityError:
                # Handle database errors (e.g., unique constraint violation)
                return render(request, 'submit_question.html', {'form': form, 'error': 'There was an error saving your question. Please try again.'})
            except Exception as e:
                # Catch any other unexpected errors
                return render(request, 'submit_question.html', {'form': form, 'error': f"An unexpected error occurred: {str(e)}"})
        else:
            # Form is not valid, return to form with error messages
            return render(request, 'submit_question.html', {'form': form, 'error': 'There are some issues with your submission. Please check the fields and try again.'})

    else:
        form = QuestionForm()

    return render(request, 'submit_question.html', {'form': form})

# Success page
def success(request):
    return HttpResponse("Your question has been successfully submitted!")