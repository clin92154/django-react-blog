from django.urls import path ,include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter

from . import views
from .views import *
"""
access token: 
    client 端可以用這組 token 來向 server 索取資料
    server 端利用這組來判斷 client 是否有被授權。時效通常不長。
refresh token: 
    refresh token 是用來索取 access token 
    當 access token 過期/存取新的 resource 時，會用來索取 access token。
    時效通常比較長。 
    
關於為什麼明明 refresh token 也有辦法得到 access token 了
那幹嘛還要兩種 token 呢? 網路上有很多解釋
主要原因是為了安全因素
refresh token 只跟 authentication server 互動
access token 會需要跟一個或多個 resource server 互動
因此 access token 有比較大的機率暴露在危險之下
因此 access token 的時效設定為比較短
直到 access token 到期後
再用 refresh token 跟 authentication 再要一次 access token。
"""


router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"^(?P<post_id>\d+)/comment", CommentViewSet) #posts/{num}/comment/  
router.register(r"", PostViewSet)

urlpatterns = [
    #jwt專用機制
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/custom_obtain/', ObtainTokenPairWithCustomView.as_view(), name='token_create_custom'),
    #前端使用
    path("register/", views.RegisterationAPIView.as_view(), name="create-user"), #used
    path("login/", views.LoginAPIView.as_view(), name="login-user"), #used
    # path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout-user"), #used
    path("user/", views.UserAPIView.as_view(), name="user-info"), 
    path("profile/", views.ProfileAPIView.as_view(), name="user-profile"), #used
    path("profile/avatar/", views.AvatarAPIView.as_view(), name="user-avatar"),

    path("like/<int:pk>/", LikePostAPIView.as_view(), name="like-post"), #used
    path("posts/", include(router.urls)), #used
    # path("profile/avatar/", views.UserAvatarAPIView.as_view(), name="user-avatar"),

]
