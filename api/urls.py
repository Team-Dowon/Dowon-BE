from django.urls import path
from .views import board_views, dictionary_views, naturalML_views, user_views

from rest_framework_simplejwt.views import TokenRefreshView

# api들 주소 정해주기.
urlpatterns = [

    path('token/refresh', TokenRefreshView.as_view()),

    path('user/register', user_views.RegisterView.as_view()),
    path('user/login', user_views.LoginView.as_view()),
    path('user/logout', user_views.LogoutView.as_view()),
    path('user', user_views.UserDetailView.as_view()),
    path('user/profile', user_views.ProfileView.as_view()),

    path('dictionary', dictionary_views.DictionaryListView.as_view()), # 초성검색
    path('dictionary/<str:dictionary_name>', dictionary_views.DictionaryDetailView.as_view()),
    path('dictionary_cho', dictionary_views.DictionaryChoView.as_view()),

    path('post', board_views.PostListView.as_view()),
    path('post/<int:post_id>', board_views.PostDetailView.as_view()),
    path('post/<int:post_id>/comment', board_views.CommentListView.as_view()),
    path('post/<int:post_id>/comment/<int:comment_id>', board_views.CommentDetailView.as_view()),
    path('request', board_views.RequestListView.as_view()),
    path('request/<int:request_id>', board_views.RequestDetailView.as_view()),

    path('sentence', naturalML_views.SentenceToNormal.as_view()),
    path('test', naturalML_views.test.as_view()),
]