from .serializers import *
from .models import *
from .forms import *

from django.http import Http404
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


# 사용자 정보
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_anonymous:
            return Response({
                "user": "User Not Found"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = UserSerializer(request.user)
            return Response({
                "user": {
                    "u_id": serializer.data["u_id"],
                    "nickname": serializer.data["nickname"],
                    "email": serializer.data["email"],
                }
            }, status=status.HTTP_200_OK)


class LoginView(APIView):  # 로그인
    def post(self, request):
        try:
            data = request.data  # 입력된 데이터를 data 저장.
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():  # 유효성 검사 -> serialize 저장 가능
                u_id = serializer.data['u_id']
                password = serializer.data['password']

                user = authenticate(u_id=u_id, password=password)  # 회원 정보 확인.

                if user is None:  # 회원 정보가 일치하지 않거나 없다면 오류 메시지
                    return Response({
                        'message': '유저가 없거나 비밀번호 틀림'
                    }, status=status.HTTP_400_BAD_REQUEST)

                refresh = RefreshToken.for_user(user)  # 유저 정보로 refresh 토큰 생성
                refresh['nickname'] = user.nickname  # refresh 토큰에 nickname 값 추가로 입력

                res = Response()  # cookie 넣기 위해 Response 사용
                res.set_cookie('jwt', str(refresh))  # jwt이름의 쿠키 value refresh 토큰으로 설정

                res.data = {
                    'nickname': str(user.nickname),
                    'message': "로그인 완료",
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                return res

            return Response({
                'message': '잘못된 응답'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):  # 회원가입
    def post(self, request):
        try:
            user = request.data  # 입력된 데이터를 user 저장.

            serializer = RegistrationSerializer(data=user)
            if User.objects.filter(nickname=request.data['nickname']).exists():  # 닉네임 중복 체크
                return Response({
                    'message': '중복되는 닉네임 입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(email=request.data['email']).exists():  # 이메일 중복 체크
                return Response({
                    'message': '중복되는 이메일 입니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.is_valid()
            serializer.save()
            return Response({
                'message': '회원가입 완료',
            }, status=status.HTTP_200_OK)
        except Exception as e:  # 예외처리
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):  # 로그아웃
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('jwt')
            if not refresh_token:
                return Response({
                    'message': '토큰이 없습니다.',
                }, status=status.HTTP_400_BAD_REQUEST)
            res = Response()
            res.delete_cookie('jwt')
            token = RefreshToken(refresh_token)
            token.blacklist()

            res.data = {'message': "로그아웃 완료"}

            return res
        except Exception as e:  # 예외처리
            return Response({
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


# class DictionaryListView(APIView):
#     def filter_object_or_404(self, condition_id):
#         try:
#             return Question.objects.filter(condition=condition_id)
#         except Question.DoesNotExist:
#             raise Http404
#
#     def get(self, request, condition_id):
#         questions = self.filter_object_or_404(condition_id)
#         serializer = QuestionSerializer(questions, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class DictionaryDetailView(APIView):
    def get_object_or_404(self, dictionary_id):
        try:
            return SDictionary.objects.get(pk=dictionary_id)
        except SDictionary.DoesNotExist:
            raise Http404

    def get(self, request, dictionary_id):
        dictionary = self.get_object_or_404(dictionary_id)
        serializer = SDictionarySerializer(dictionary)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        title = request.data["title"]
        content = request.data["content"]

        data = {
            "user": user,
            "title": title,
            "content": content,
        }

        form = PostForm(data=data)

        if form.is_valid():
            form.save()

            return Response("Post Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    def get_object_or_404(self, post_id):
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        post = self.get_object_or_404(post_id)

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id):
        cur_post = self.get_object_or_404(post_id)

        user = User.objects.get(id=request.user.id)
        title = request.data["title"]
        content = request.data["content"]

        data = {
            "user": user,
            "title": title,
            "content": content,
        }

        if cur_post.user == request.user:
            form = PostForm(data=data, instance=cur_post)

            if form.is_valid():
                form.save()

                return Response("Post Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = self.get_object_or_404(post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListView(APIView):
    def filter_object_or_404(self, post_id):
        try:
            return Comment.objects.filter(post=post_id)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        comments = self.filter_object_or_404(post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        user = User.objects.get(id=request.user.id)
        content = request.data["content"]

        data = {
            "user": user,
            "post": post_id,
            "content": content,
        }

        form = CommentForm(data=data)

        if form.is_valid():
            form.save()

            return Response("Comment Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    def get_object_or_404(self, post_id, comment_id):
        try:
            return Comment.objects.get(post=post_id, pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, post_id, comment_id):
        comment = self.get_object_or_404(post_id, comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id, comment_id):
        cur_comment = self.get_object_or_404(post_id, comment_id)

        user = User.objects.get(id=request.user.id)
        content = request.data["content"]

        data = {
            "user": user,
            "post": post_id,
            "content": content,
        }

        if cur_comment.user == request.user:
            form = CommentForm(data=data, instance=cur_comment)

            if form.is_valid():
                form.save()

                return Response("Comment Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        comment = self.get_object_or_404(post_id, comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestListView(APIView):
    def get(self, request):
        requests = Request.objects.all()
        serializer = RequestSerializer(requests)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        title = request.data["title"]
        content = request.data["content"]
        name = request.data["name"]

        data = {
            "user": user,
            "title": title,
            "content": content,
            "name": name,
        }

        form = RequestForm(data=data)

        if form.is_valid():
            form.save()

            return Response("Request Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestDetailView(APIView):
    def get_object_or_404(self, request_id):
        try:
            return Request.objects.get(pk=request_id)
        except Request.DoesNotExist:
            raise Http404

    def get(self, request, request_id):
        request = self.get_object_or_404(request_id)

        serializer = RequestSerializer(request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, request_id):
        cur_request = self.get_object_or_404(request_id)

        user = User.objects.get(id=request.user.id)
        title = request.data["title"]
        content = request.data["content"]
        name = request.data["name"]

        data = {
            "user": user,
            "title": title,
            "content": content,
            "name": name,
        }

        if cur_request.user == request.user:
            form = RequestForm(data=data, instance=cur_request)

            if form.is_valid():
                form.save()

                return Response("Request Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, request_id):
        request = self.get_object_or_404(request_id)
        request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)