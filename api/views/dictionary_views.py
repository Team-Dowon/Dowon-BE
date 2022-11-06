from api.serializers import *
from api.forms import *

from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class DictionaryListView(APIView):  # 사전 리스트 초성 검색
    def filter_object_or_404(self, search):     # search가 들어가 있는 단어 가져오기
        try:
            return SDictionary.objects.filter(name__contains=search)
        except SDictionary.DoesNotExist:
            raise Http404

    def post(self, request):    # 초성으로 입력되면 초성 검색, 아니면 이름 검색
        k = 0
        dictionaries = SDictionary.objects.filter(pk=0)     # 임시 사전 구축
        search = request.data["search"]     # 입력 데이터 저장
        ascii_values = [ord(character) for character in search]     # 입력된 초성 만큼 저장.
        for cho in ascii_values:    # 입력된 초성 만큼 반복
            k = k + 1
            if 12593 <= cho & cho <= 12622:     # 입력 된 값이 초성이면 ㄱ 을 가 ㄴ 을 나로
                if cho < ord('ㅅ'):
                    d = {ord('ㄱ'): ord('가'), ord('ㄲ'): ord('까'), ord('ㄴ'): ord('나'), ord('ㄷ'): ord('다'), ord('ㄸ'): ord('따'), ord('ㄹ'): ord('라'),
                         ord('ㅁ'): ord('마'), ord('ㅂ'): ord('바'), ord('ㅃ'): ord('빠')}
                    cho2 = d.get(cho) # 초성 가져오기
                else:
                    cho2 = (cho - 12604) * 588 + 44032  # 위의 값이 아닌 ㅅ ~ ㅎ등은 따로 설정
                if k > 1:
                    dictionaries1 = SDictionary.objects.filter(pk=0)    # 입력 된 초성이 2개 이상이면
                    for i in range(588):
                        dictionaries2 = SDictionary.objects.filter(name__contains=chr(cho2 + i))    # 입력 된 초성 값으로 찾기
                        dictionaries1 = dictionaries1 | dictionaries2   # 두개 같이 검색
                    dictionaries = dictionaries & dictionaries1     # 초성 합치기 검색
                else:
                    for i in range(588):    # 하나만 입력된 경우
                        dictionaries2 = SDictionary.objects.filter(name__contains=chr(cho2 + i))    # 입력 된 초성 값으로 찾기
                        dictionaries = dictionaries | dictionaries2     # 합치기
            else:
                dictionaries = self.filter_object_or_404(search)
        serializer = SDictionarySerializer(dictionaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DictionaryDetailView(APIView):    # 특정 사전 단어 검색
    def get_object_or_404(self, dictionary_name):   # 이름이 정확히 일치하게 검색
        try:
            return SDictionary.objects.get(name=dictionary_name)
        except SDictionary.DoesNotExist:
            raise Http404

    def get(self, request, dictionary_name):    # 특정 사전 단어 가져오기
        dictionary = self.get_object_or_404(dictionary_name)
        serializer = SDictionarySerializer(dictionary)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DictionaryChoView(APIView):   # 첫번째 초성만 검색
    def post(self, request):
        cho = ord(request.data["cho"])  # 초성을 숫자로 변경
        if 12593 <= cho & cho <= 12622:     # 초성이 맞는지 확인
            if cho < ord('ㅅ'):
                d = {ord('ㄱ'): ord('가'), ord('ㄲ'): ord('까'), ord('ㄴ'): ord('나'), ord('ㄷ'): ord('다'), ord('ㄸ'): ord('따'), ord('ㄹ'): ord('라'), ord('ㅁ'): ord('마'), ord('ㅂ'): ord('바'), ord('ㅃ'): ord('빠')}
                cho = d.get(cho)
            else:
                cho = (cho - 12604) * 588 + 44032   # 위의 초성이 아니면 함수로 바꾸기
            dictionaries = SDictionary.objects.filter(pk=0)
            for i in range(588):
                dictionary = SDictionary.objects.filter(name__istartswith=chr(cho + i))     # 초성 찾기
                dictionaries = dictionaries | dictionary    # 찾은 것 합치기
            serializer = SDictionarySerializer(dictionaries, many=True)     # 시리얼 라이즈 데이터로 저장
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': '초성이 아닙니다.'
            }, status=status.HTTP_400_BAD_REQUEST)