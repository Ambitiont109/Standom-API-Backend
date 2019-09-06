from rest_framework import serializers
from .models import User, Question


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    auth_type = serializers.CharField()  # available value: basci, google, facebook
    password = serializers.CharField(required=False)
    latitude = serializers.FloatField(default=0.0)
    longitude = serializers.FloatField(default=0.0)

    def validate(self, data):
        """
        Validate the Input according to the auth_type
        if auth_type is equal to 'basic', the password field is required
        """
        if(data['auth_type'] == 'basic'):
            password = data.get('password', None)
            if password is None:
                raise serializers.ValidationError({"password": "this field is required"})
        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'password')
        extra_kwargs = {'name': {'required': True},
                        'email': {'required': True},
                        'password': {'required': True}
                        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.username = validated_data['email']
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'avatar', 'latitude', 'longitude', 'score')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['avatar']:
            data['avatar'] = ""
        else:
            data['avatar'] = data['avatar'][1:]
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'avatar')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['avatar']:
            data['avatar'] = ""
        else:
            data['avatar'] = data['avatar'][1:]
        return data



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
