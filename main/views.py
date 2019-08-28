from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from .serializers import LoginSerializer, RegisterSerializer, QuestionSerializer, UserSerializer, UserUpdateSerializer
from .models import User, Question, Answer


def format_errors(errors, res_status = False):
    for key in errors:
        errors[key] = errors[key][0]
    errors['res'] = res_status
    return errors


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        auth_type = serializer.validated_data['auth_type']
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
            user = User.objects.get_or_create(email=email, username=email)
            user[0].save()
            user = user[0]
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
def list_question(request):
    ret_val = {}
    if request.user.is_in_location():
        serializer = QuestionSerializer(Question.objects.all(), many=True)
        ret_val['questions'] = serializer.data
        ret_val['res'] = True
    else:
        ret_val['res'] = False
        ret_val['error'] = 'The user is not in 10km radius'
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
def list_user(request):
    """
    List users order by score
    """
    serializer = UserSerializer(User.objects.filter(is_superuser=False).order_by('score').all(), many=True)
    ret_val = serializer.data
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
