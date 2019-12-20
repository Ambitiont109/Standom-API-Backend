from django import forms
from main.models import Question, AvailabeAnswer
from django.forms.models import inlineformset_factory


class AvailabeAnswerForm(forms.ModelForm):

    class Meta:
        model = AvailabeAnswer
        fields = '__all__'


AnswerInlineForm = inlineformset_factory(Question, AvailabeAnswer, form=AvailabeAnswerForm, can_delete=True, extra = 2)


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = '__all__'
