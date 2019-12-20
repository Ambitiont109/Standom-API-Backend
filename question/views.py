from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from main.models import Question, AvailabeAnswer
from .forms import AnswerInlineForm, QuestionForm
from django.db import transaction

# Create your views here.


@login_required
def add_question_view(request, campaign_pk):
    answerInlineForm = AnswerInlineForm()

    questionForm = QuestionForm(initial={'campaign': campaign_pk})
    # print(questionInlineForm)
    if request.method == 'POST':
        answerInlineForm = AnswerInlineForm(request.POST)
        data = request.POST.dict()
        data['campaign'] = campaign_pk
        questionForm = QuestionForm(data= data)

        if answerInlineForm.is_valid() and questionForm.is_valid():
            with transaction.atomic():
                question = questionForm.save()
                answerInlineForm.instance = question
                answerInlineForm.save()
                messages.add_message(request, messages.SUCCESS, 'Question Added Successfully')
            return redirect('campaign:detail_campaign', campaign_pk)
    return render(request, 'question/update.html', {'formset': answerInlineForm, 'questionForm': questionForm, 'campaign_pk': campaign_pk})


@login_required
def edit_question_view(request, question_pk):
    question = Question.objects.filter(pk=question_pk).first()
    answerInlineForm = AnswerInlineForm(instance=question)
    print(request.POST)
    questionForm = QuestionForm(instance=question)
    if request.method == 'POST':
        answerInlineForm = AnswerInlineForm(instance=question, data=request.POST)
        questionForm = QuestionForm(instance=question, data = request.POST)
        print(answerInlineForm.errors)
        form = answerInlineForm[0]
        print(form)
        print(form.fields)
        print(form.fields['answer'])
        if answerInlineForm.is_valid() and questionForm.is_valid():
            with transaction.atomic():
                answerInlineForm.save()
                messages.add_message(request, messages.SUCCESS, 'Question Updated Successfully')
            return redirect('campaign:detail_campaign', question.campaign.id)
    return render(request, 'question/update.html', {'formset': answerInlineForm, 'questionForm': questionForm})


@login_required
def delete_question_view(request, campaign_pk, question_pk):
    if request.method == 'POST':
        campaign = get_object_or_404(Question.objects.all(), pk=question_pk)
        campaign.delete()
        messages.add_message(request, messages.SUCCESS, 'Question Deleted Successfully')
        return redirect('campaign:detail_campaign', campaign_pk)
