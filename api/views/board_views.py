from rest_framework.permissions import IsAuthenticated

from api.serializers import *
from api.forms import *

from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class PostListView(APIView):    # 포스트 리스트 가져오기, 입력 뷰
    def get(self, request): # 포스트 값 가져오기
        posts = Post.objects.all()  # 모든 포스트 값 가져오기
        serializer = PostSerializer(posts, many=True)   # serializer 설정
        return Response(serializer.data, status=status.HTTP_200_OK) # 프론트로 보네기

    def post(self, request):    # 포스트 값 입력하기
        user = User.objects.get(id=request.user.id) # 로그인 된 유저 찾기
        title = request.data["title"]   # 입력 데이터 저장
        content = request.data["content"]

        data = {
            "user": user,
            "title": title,
            "content": content,
        }

        form = PostForm(data=data)  # 폼으로 임시 저장

        if form.is_valid():     # 폼이 유효하면 저장
            form.save()

            return Response("Post Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):      # 특정 포스트 가져오기, 변경, 삭제 뷰
    def get_object_or_404(self, post_id):   # post id로 오브젝트 찾기
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):    # 포스트 아이디로 특정 포스트 찾기
        post = self.get_object_or_404(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id):    # 포스트 값 바꾸기
        cur_post = self.get_object_or_404(post_id)
        user = User.objects.get(id=request.user.id)
        title = request.data["title"]   # 입력 데이터 저장
        content = request.data["content"]

        data = {
            "user": user,
            "title": title,
            "content": content,
        }

        if cur_post.user == request.user:   # 현재 유저가 적은 글이 맞는지 확인
            form = PostForm(data=data, instance=cur_post)   # 폼으로 임시저장

            if form.is_valid():     # 폼이 유효하면 저장
                form.save()

                return Response("Post Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):     # 특정 포스트 삭제하기
        post = self.get_object_or_404(post_id)
        if post.user == request.user:   # 현재 유저가 적은 글이 맞는지 확인 후 삭제
            post.delete()
            return Response(f"A{post_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)


class CommentListView(APIView):     # 댓글 리스트 가져오기, 입력 뷰
    def filter_object_or_404(self, post_id):    # 포스트 아이디로 댓글들 찾기
        try:
            return Comment.objects.filter(post=post_id)     # 특정 포스트에 있는 댓글만 찾기
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, post_id):    # 특정 포스트의 댓글들 가져오기
        comments = self.filter_object_or_404(post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):   # 특정 포스트에 댓글 입력하기
        user = User.objects.get(id=request.user.id)     # 현재 유저 정보 자동 입력
        content = request.data["content"]   # 입력 데이터 저장

        data = {
            "user": user,
            "post": post_id,
            "content": content,
        }

        form = CommentForm(data=data)   # 폼으로 임시 저장

        if form.is_valid():     # 폼이 유효하다면 저장
            form.save()

            return Response("Comment Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):   # 특정 댓글 가져오기, 변경, 삭제 뷰
    def get_object_or_404(self, post_id, comment_id):   # 특정 댓글 오브젝트 가져오기
        try:
            return Comment.objects.get(post=post_id, pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, post_id, comment_id):    # 특정 댓글 확인
        comment = self.get_object_or_404(post_id, comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, post_id, comment_id):    # 특정 댓글 변경하기
        cur_comment = self.get_object_or_404(post_id, comment_id)
        user = User.objects.get(id=request.user.id)     # 유저 정보 자동 입력
        content = request.data["content"]   # 입력 데이터 저장

        data = {
            "user": user,
            "post": post_id,
            "content": content,
        }

        if cur_comment.user == request.user:    # 유저 확인, 맞다면 폼으로 임시 저장
            form = CommentForm(data=data, instance=cur_comment)

            if form.is_valid():     # 폼 유효하면 저장
                form.save()

                return Response("Comment Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):     # 댓글 삭제하기
        comment = self.get_object_or_404(post_id, comment_id)
        if comment.user == request.user:    # 유저 확인, 맞다면 삭제
            comment.delete()
            return Response(f"A{comment_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)


class RequestListView(APIView):      # 댓글 리스트 가져오기, 입력 뷰
    def get(self, request):     # 댓글 리스트 가져오기
        requests = Request.objects.all()    # 모든 댓글 오브젝트
        serializer = RequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):    # 댓글 입력하기
        user = User.objects.get(id=request.user.id)     # 현재 유저 정보
        title = request.data["title"]   # 입력 데이터 저장
        content = request.data["content"]
        name = request.data["name"]

        data = {
            "user": user,
            "title": title,
            "content": content,
            "name": name,
        }

        form = RequestForm(data=data)   # 폼 임시 저장

        if form.is_valid():     # 폼이 유효하다면 저장
            form.save()

            return Response("Request Submitted", status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestDetailView(APIView):   # 특정 댓글 가져오기, 변경, 삭제 뷰
    def get_object_or_404(self, request_id):    # 특정 요청 가져오기
        try:
            return Request.objects.get(pk=request_id)
        except Request.DoesNotExist:
            raise Http404

    def get(self, request, request_id):     # 특정 요청 시리얼 라이즈 데이터로 가져오기
        request1 = self.get_object_or_404(request_id)

        serializer = RequestSerializer(request1)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, request_id):     # 특정 요청 변경하기
        cur_request = self.get_object_or_404(request_id)
        user = User.objects.get(id=request.user.id)     # 현재 유저 정보 입력
        title = request.data["title"]   # 입력 데이터 저장
        content = request.data["content"]
        name = request.data["name"]

        data = {
            "user": user,
            "title": title,
            "content": content,
            "name": name,
        }

        if cur_request.user == request.user:    # 현재 유저 정보와 요청의 유저 정보 일치 확인후 폼 임시 저장
            form = RequestForm(data=data, instance=cur_request)

            if form.is_valid():     # 폼이 유효하다면 저장
                form.save()

                return Response("Request Edited", status=status.HTTP_201_CREATED)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, request_id):  # 요청 삭제하기
        request1 = self.get_object_or_404(request_id)
        if request1.user == request.user:   # 현재 유저 정보와 요청의 유저 정보 일치 확인후 특정 요청 삭제
            request1.delete()
            return Response(f"A{request_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)


class RequestLikeView(APIView):   # 유저 프로필 사진
    permission_classes = [IsAuthenticated]  # 로그인 확인

    def get_object_or_404(self, request_id):    # 특정 요청 가져오기
        try:
            return Request.objects.get(pk=request_id)
        except Request.DoesNotExist:
            raise Http404

    def post(self, request, request_id):
        request1 = self.get_object_or_404(request_id)

        if request1.like_users.filter(pk=request.user.pk).exists():
            request1.like_users.remove(request.user)
            return Response({
                'message': '좋아요 취소'
            }, status=status.HTTP_200_OK)
        else:
            request1.like_users.add(request.user)
            return Response({
                'message': '좋아요'
            }, status=status.HTTP_200_OK)

