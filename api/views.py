from dowonpackage.tag import Okt
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from .models import *
from .forms import *

from django.http import Http404
from django.contrib.auth import authenticate
from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import re
import json
from dowonpackage.tag import Okt
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import pickle
import keras

# 사용자 정보
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_anonymous:
            return Response({
                "user": "User Not Found"
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)


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


class DictionaryListView(APIView):
    def filter_object_or_404(self, search):
        try:
            return SDictionary.objects.filter(name__contains=search)
        except SDictionary.DoesNotExist:
            raise Http404

    def post(self, request):
        k = 0
        dictionaries = SDictionary.objects.filter(pk=0)
        search = request.data["search"]
        ascii_values = [ord(character) for character in search]
        for cho in ascii_values:
            k = k + 1
            if 12593 <= cho & cho <= 12622:
                if cho < ord('ㅅ'):
                    d = {ord('ㄱ'): ord('가'), ord('ㄲ'): ord('까'), ord('ㄴ'): ord('나'), ord('ㄷ'): ord('다'), ord('ㄸ'): ord('따'), ord('ㄹ'): ord('라'), 
                         ord('ㅁ'): ord('마'), ord('ㅂ'): ord('바'), ord('ㅃ'): ord('빠')}
                    cho2 = d.get(cho)
                else:
                    cho2 = (cho - 12604) * 588 + 44032
                if k > 1:
                    dictionaries1 = SDictionary.objects.filter(pk=0)
                    for i in range(588):
                        dictionaries2 = SDictionary.objects.filter(name__contains=chr(cho2 + i))
                        dictionaries1 = dictionaries1 | dictionaries2
                    dictionaries = dictionaries & dictionaries1
                else:
                    for i in range(588):
                        dictionaries2 = SDictionary.objects.filter(name__contains=chr(cho2 + i))
                        dictionaries = dictionaries | dictionaries2
            else:
                dictionaries = self.filter_object_or_404(search)
        serializer = SDictionarySerializer(dictionaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DictionaryDetailView(APIView):
    def get_object_or_404(self, dictionary_name):
        try:
            return SDictionary.objects.get(name=dictionary_name)
        except SDictionary.DoesNotExist:
            raise Http404

    def get(self, request, dictionary_name):
        dictionary = self.get_object_or_404(dictionary_name)
        serializer = SDictionarySerializer(dictionary)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DictionaryChoView(APIView):
    def filter_object_or_404(self, search):
        try:
            return SDictionary.objects.filter(name__contains=search)
        except SDictionary.DoesNotExist:
            raise Http404

    def post(self, request):
        k = 0
        dictionaries = SDictionary.objects.filter(pk=0)
        search = request.data["search"]
        ascii_values = [ord(character) for character in search]
        for cho in ascii_values:
            k = k + 1
            if 12593 <= cho & cho <= 12622:
                if cho < ord('ㅅ'):
                    d = {ord('ㄱ'): ord('가'), ord('ㄲ'): ord('까'), ord('ㄴ'): ord('나'), ord('ㄷ'): ord('다'), ord('ㄸ'): ord('따'), ord('ㄹ'): ord('라'),
                         ord('ㅁ'): ord('마'), ord('ㅂ'): ord('바'), ord('ㅃ'): ord('빠')}
                    cho2 = d.get(cho),
                else:
                    cho2 = (cho - 12604) * 588 + 44032
                if k > 1:
                    dictionaries1 = SDictionary.objects.filter(pk=0)
                    for i in range(588):
                        dictionaries2 = SDictionary.objects.filter(name__istartswith=chr(cho2 + i))
                        dictionaries1 = dictionaries1 | dictionaries2
                    dictionaries = dictionaries & dictionaries1
                else:
                    for i in range(588):
                        dictionaries2 = SDictionary.objects.filter(name__istartswith=chr(cho2 + i))
                        dictionaries = dictionaries | dictionaries2
            else:
                dictionaries = self.filter_object_or_404(search)
        serializer = SDictionarySerializer(dictionaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class SentenceToNormal(APIView):
    def post(self, request):
        try:
            okt = Okt()

            # 입력할 문장
            text = request.data['text']

            # text에서 형태소 반환
            morphs = okt.morphs(text)

            # 신조어 목록 텍스트 파일 읽어오기
            textFile = open("ListSlang.txt", 'r', encoding='UTF8')

            # 신조어들 배열로 받을 빈 배열 생성
            slanglist = []

            # ListSlang.txt에 적혀있는 신조어들 slanglist배열에 한 단어씩 append
            while True:
                slang = textFile.readline()
                if not slang:
                    break
                slanglist.append(slang.strip())

            doslang = []
            # 반환된 형태소들 중 신조어 목록에 있는 단어와 일치하는 단어가 있으면 출력
            for extraction in morphs:
                if str(extraction) in slanglist:
                    doslang.append(str(extraction))

            # text에 적힌 문장 속 신조어들 이해하기 쉽게 변환
            normalize = okt.normalize(text)

            textFile.close()

            # text에서 명사를 반환
            # nouns=okt.nouns(text)
            # print(nouns)

            # text에서 품사 정보 부착하여 반환
            # print(okt.pos(text))

            return JsonResponse({'morphs': morphs, 'doslang': doslang, 'normalize': normalize}, status=200)
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


def sum_list(lst, res=0):
    for i in lst:
        if type(i) == list:
            res += sum_list(i)
        else:
            res += i
    return res


class test(APIView):
    def post(self, request):
        try:
            okt = Okt()
            tokenizer = Tokenizer()

            DATA_CONFIGS = 'data_configs.json'
            prepro_configs = json.load(
                open('./emo_module/CLEAN_DATA/' + DATA_CONFIGS, 'r', encoding='cp949'))  # TODO 데이터 경로 설정

            # TODO 데이터 경로 설정
            with open('./emo_module/CLEAN_DATA/tokenizer.pickle', 'rb') as handle:
                word_vocab = pickle.load(handle)

            prepro_configs['vocab'] = word_vocab

            tokenizer.fit_on_texts(word_vocab)

            MAX_LENGTH = 8  # 문장최대길이

            while True:
                sentence = request.data['sentence']
                if sentence == '끝':
                    break
                sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]', '', sentence)
                stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등',
                             '한']  # 불용어 추가할 것이 있으면 이곳에 추가
                sentence = okt.morphs(sentence, stem=True)  # 토큰화
                sentence = [word for word in sentence if not word in stopwords]  # 불용어 제거
                vector = tokenizer.texts_to_sequences(sentence)
                pad_new = pad_sequences(vector, maxlen=MAX_LENGTH)  # 패딩

                # 학습한 모델 불러오기
                model = keras.models.load_model('./emo_module/my_models/')  # TODO 데이터 경로 설정
                model.load_weights('./emo_module/DATA_OUT/cnn_classifier_kr/weights.h5')  # TODO 데이터 경로 설정
                predictions = model.predict(pad_new)
                print(predictions)
                predictions = float(sum_list(predictions) / len(predictions))
                # predictions = float(predictions.squeeze(-1)[1])

                if (predictions > 0.5):
                    print("{:.2f}% 확률로 긍정 리뷰입니다.\n".format(predictions * 100))
                    emotion = '긍정'
                else:
                    print("{:.2f}% 확률로 부정 리뷰입니다.\n".format((1 - predictions) * 100))
                    emotion = '부정'

                return JsonResponse({'예측값': emotion}, status=200)
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)