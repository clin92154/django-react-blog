from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password #設定密碼規範
from django.contrib.auth import authenticate

from .models import *


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        token['bio'] = "你好"
        return token


###
#註冊及登入
#
####


class LoginSerializer(serializers.Serializer):
    """
    Serializer class to authenticate users with email and password.
    """

    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])    
    class Meta:
        model = User
        fields = ('email', 'password',)
    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            password=make_password(validated_data['password'], salt=None, hasher='bcrypt_sha256')
        )
        user.save()
        return user
    

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize CustomUser model.
    """

    class Meta:
        model = User
        # fields = "__all__"
        exclude = ["groups","user_permissions","createtime","is_superuser","is_staff","is_active"]



class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the user Profile model
    """
    class Meta:
        model = Profile
        fields = "__all__"


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the avatar
    """

    class Meta:
        model = Profile
        fields = ("profile_pic",)



class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



#讀取Post
class PostReadSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.id", read_only=True)
    categories = serializers.SerializerMethodField(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

    def get_categories(self, obj):
        categories = list(
            cat.name for cat in obj.categories.get_queryset().only("name")
        )
        return categories

    def get_author(self, obj):
        author = list(
            author.id for author in obj.author.get_queryset().only("id")
        )
        return author

    def get_likes(self, obj):
        likes = list(
            like.id for like in obj.likes.get_queryset().only("id")
        )
        return likes
    
    def get_comments(self,obj):
        comments = obj.comments
        return comments


class PostWriteSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Post
        fields = "__all__"

class CommentReadSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.id", read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"

class CommentWriteSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = "__all__"
