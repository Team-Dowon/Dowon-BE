from rest_framework import serializers
from .models import *


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = KDictionary
        fields = '__all__'


class SDictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SDictionary
        fields = '__all__'


class KDictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = KDictionary
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname')
    user_profile_pic = serializers.ImageField(source='user.profile_pic')

    class Meta:
        model = Request
        fields = ('id', 'user_nickname', 'title', 'content', 'name', 'date')


class PostSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname')
    user_profile_pic = serializers.ImageField(source='user.profile_pic')

    class Meta:
        model = Post
        fields = ('id', 'user_nickname', 'title', 'content', 'date')


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname')
    user_profile_pic = serializers.ImageField(source='user.profile_pic')

    class Meta:
        model = Comment
        fields = ('id', 'post', 'user_nickname', 'content', 'date')


class AnalyzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyzer
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'u_id',
            'nickname',
            'email',
            'profile_pic',
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            # provide django, password will be hashing!
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    u_id = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['u_id', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_pic']