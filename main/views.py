from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from .serializers import LoginSerializer, RegisterSerializer, QuestionSerializer, UserSerializer, UserUpdateSerializer
from .models import User, Question, Answer
from .decorators import get_gps_location
from .forms import LoginForm


def format_errors(errors, res_status = False):
    for key in errors:
        errors[key] = errors[key][0]
    errors['res'] = res_status
    return errors


@api_view(['POST'])
def loginApi(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        auth_type = serializer.validated_data['auth_type']
        lat = serializer.validated_data['latitude']
        lng = serializer.validated_data['longitude']
        user = None
        if auth_type == "basic":
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'error': 'email or password is invalid', 'res': False}, status=status.HTTP_200_OK)
            pwd = serializer.validated_data['password']
            if not user.check_password(pwd):
                return Response({'error': 'email or password is invalid', 'res': False}, status=status.HTTP_200_OK)
        else:
            name = serializer.validated_data['name']
            user = User.objects.get_or_create(email=email, username=email)
            user[0].save()
            user = user[0]
        user.latitude = lat
        user.longitude = lng
        user.save()
        token = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        res_val = serializer.data
        if res_val['avatar'] is None:
            res_val['avatar'] = ''
        res_val['token'] = token[0].key
        res_val['res'] = True
        return Response(res_val, status=status.HTTP_200_OK)
    res_val = serializer.errors
    format_errors(res_val)
    return Response(res_val, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "created", 'res': True}, status=status.HTTP_200_OK)
    res_val = serializer.errors
    format_errors(res_val)
    return Response(res_val, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@get_gps_location
def list_question(request):
    ret_val = {}
    campaign = request.user.get_campaign_in_location()
    if campaign:
        serializer = QuestionSerializer(campaign.question_set.exclude(answers__user=request.user), many=True)
        ret_val['questions'] = serializer.data
        ret_val['res'] = True
    else:
        ret_val['res'] = False
        ret_val['error'] = 'The user is out of range'
    return Response(ret_val, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def check_answer(request):
    try:
        question_id = request.data['question_id']
        answer = request.data['answer']
    except Exception:
        return Response({'error': 'Must include question_id and answer', 'res': False}, status=status.HTTP_200_OK)
    try:
        question_obj = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        return Response({'error': "Question %d is not exist" % (question_id, ), 'res': False}, status=status.HTTP_200_OK)
    answer_obj = Answer.objects.get_or_create(user=request.user, question = question_obj)[0]
    answer_obj.answer = answer
    answer_obj.save()
    return Response({"message": "Answer Has Been Submitted", 'res': True}, status=status.HTTP_200_OK)
    # if question_obj.check_answer(answer) is True:
    #     answer_obj.is_right = True
    #     answer_obj.save()
    #     request.user.update_score()
    #     request.user.save()
    #     return Response({"message": "Right", 'res': True}, status=status.HTTP_200_OK)
    # else:
    #     answer_obj.is_right = False
    #     answer_obj.save()
    #     request.user.update_score()
    #     request.user.save()
    #     return Response({"message": "Wrong", 'res': True}, status = status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@get_gps_location
def list_user(request):
    """
    List users order by score
    """
    serializer = UserSerializer(User.objects.filter(is_superuser=False).order_by('-score').all(), many=True)
    ret_val = {}
    ret_val['users'] = serializer.data
    ret_val['res'] = True
    return Response(ret_val, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def update_user(request):
    """
    List users order by score
    """
    serializer = UserUpdateSerializer(data = request.data, instance =request.user)
    ret_val = {}
    if serializer.is_valid():
        serializer.save()
        ret_val = serializer.data
        ret_val['res'] = True
    else:
        ret_val = format_errors(serializer.errors)
    return Response(ret_val, status=status.HTTP_200_OK)


def login_view(request):
    form = LoginForm(request.POST)
    error = ''
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request=request, username=email, password=password)
        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'main:list_user')
            return redirect(redirect_url)
        error = 'Invalid Credential'
    print(error)
    return render(request, 'login.html', {'form': form, 'error': error})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/admin/login')

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'main/list_user.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = super(UserListView, self).get_queryset()
        return qs.filter(is_superuser=False)


class UserCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/update.html'
    success_url = reverse_lazy('main:list_user')
    model = User
    fields = ('name', 'email', 'avatar')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.username = self.object.email
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Campaign Added Succesfully')
        return redirect(self.get_success_url())


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'main/update.html'
    success_url = reverse_lazy('main:list_user')
    model = User
    fields = ('name', 'email', 'avatar')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.username = self.object.email
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Campaign Updated Succesfully')
        return redirect(self.get_success_url())

@login_required
def delete_user_view(request, pk):
    if request.method == 'POST':
        campaign = get_object_or_404(User.objects.exclude(is_superuser=True), pk=pk)
        campaign.delete()
        messages.add_message(request, messages.SUCCESS, 'Campaign Deleted Successfully')
        return redirect('main:list_user')


@login_required
def detail_user_view(request, pk):
    if request.method == 'GET':
        user = get_object_or_404(User.objects.all(), pk=pk)
        return render(request, 'main/detail.html', {'user': user, 'answers': user.answer_set.all()})


@login_required
def detail_answer_view(request, pk):
    answer = get_object_or_404(Answer.objects.all(), pk=pk)
    if request.method == 'GET':
        return render(request, 'main/detail_answer.html', {'answer': answer})
    if request.method == 'POST':
        is_right = request.POST.get('is_right', False)
        print(request.POST)
        answer.is_right = is_right
        answer.save()
        answer.user.update_score()
        answer.user.save()
        return redirect('main:detail_user', answer.user.id)
