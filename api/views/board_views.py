from api.serializers import *
from api.forms import *

from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
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
        if post.user == request.user:
            post.delete()
            return Response(f"A{post_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)


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
        if comment.user == request.user:
            comment.delete()
            return Response(f"A{comment_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)


class RequestListView(APIView):
    def get(self, request):
        requests = Request.objects.all()
        serializer = RequestSerializer(requests, many=True)
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
        request1 = self.get_object_or_404(request_id)

        serializer = RequestSerializer(request1)
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
        request1 = self.get_object_or_404(request_id)
        if request1.user == request.user:
            request1.delete()
            return Response(f"A{request_id} Deleted", status=status.HTTP_200_OK)
        return Response("Not allowed user", status=status.HTTP_400_BAD_REQUEST)
