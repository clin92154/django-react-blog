from rest_framework.viewsets import (ReadOnlyModelViewSet,ModelViewSet)
from rest_framework import permissions
from .permissions import IsAuthorOrReadOnly
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.contrib.auth.hashers import check_password



class ObtainTokenPairWithCustomView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class RegisterationAPIView(GenericAPIView):
    """
    An endpoint for the client to create a new User.
    """

    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)

class LoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)

class LogoutAPIView(GenericAPIView):
    """
    An endpoint to logout users.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user information
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        if request.method == "PUT":
            if "oldPwd" in request.data:
                old_pwd = request.data["oldPwd"]
                if check_password(old_pwd, user.password ,'bcrypt_sha256'):
                    user.password = make_password(request.data['password'],hasher='bcrypt_sha256')
                    user.save()
                    return Response({"message": "update sucess"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "password is wrong"}, status=status.HTTP_200_OK)

class ProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        return self.request.user.profile


    
class AvatarAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileAvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile
    
    def put(self, request, *args, **kwargs):
        profile = self.request.user.profile
        profile.profile_pic = request.FILES.get('profile_pic')

        profile.save()

        return Response({"profile_pic": str(self.request.user.profile.profile_pic)}, status=status.HTTP_200_OK)

class CategoryViewSet(ReadOnlyModelViewSet):
    """
    List and Retrieve post categories
    """

    queryset = Category.objects.all()
    serializer_class = CategoryReadSerializer
    permission_classes = (permissions.AllowAny,)




class PostViewSet(ModelViewSet):
    """
    CRUD posts
    """
    queryset = Post.objects.all()

    # In order to use different serializers for different 
    # actions, you can override the 
    # get_serializer_class(self) method
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return PostWriteSerializer

        return PostReadSerializer

    # get_permissions(self) method helps you separate 
    # permissions for different actions inside the same view.
    def get_permissions(self):
        if self.action in ("create",):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = (IsAuthorOrReadOnly,)
        else:
            self.permission_classes = (permissions.AllowAny,)

        return super().get_permissions()

class CommentViewSet(ModelViewSet):
    """
    CRUD comments for a particular post
    """

    queryset = Comment.objects.all()

    def get_queryset(self):
        res = super().get_queryset()
        post_id = self.kwargs.get("post_id")
        return res.filter(post__id=post_id)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return CommentWriteSerializer

        return CommentReadSerializer

    def get_permissions(self):
        if self.action in ("create",):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = (IsAuthorOrReadOnly,)
        else:
            self.permission_classes = (permissions.AllowAny,)

        return super().get_permissions()

# Here, we are using the normal APIView class

class LikePostAPIView(APIView):
    """
    Like, Dislike a post
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        if user in post.likes.all():
            post.likes.remove(user)

        else:
            post.likes.add(user)

        return Response(status=status.HTTP_200_OK)