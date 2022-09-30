from django.urls import path
from .views import *

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    path('token/refresh', TokenRefreshView.as_view()),

    path('user/register', RegisterView.as_view()),
    path('user/login', LoginView.as_view()),
    path('user/logout', LogoutView.as_view()),

    path('user', UserDetailView.as_view()),

    path('dictionary', DictionaryListView.as_view()), # 초성검색
    path('dictionary/<str:dictionary_name>', DictionaryDetailView.as_view()),

    path('post', PostListView.as_view()),
    path('post/<int:post_id>', PostDetailView.as_view()),

    path('post/<int:post_id>/comment', CommentListView.as_view()),
    path('post/<int:post_id>/comment/<int:comment_id>', CommentDetailView.as_view()),

    path('request', RequestListView.as_view()),
    path('request/<int:request_id>', RequestDetailView.as_view()),

    path('sentence', SentenceToNormal.as_view()),
]