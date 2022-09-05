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
    request_vote = VoteSerializer(many=False)

    class Meta:
        model = Request
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


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
