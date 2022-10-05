from api.serializers import *
from api.forms import *

from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


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
    def post(self, request):
        cho = ord(request.data["cho"])
        if 12593 <= cho & cho <= 12622:
            if cho < ord('ㅅ'):
                d = {ord('ㄱ'): ord('가'), ord('ㄲ'): ord('까'), ord('ㄴ'): ord('나'), ord('ㄷ'): ord('다'), ord('ㄸ'): ord('따'), ord('ㄹ'): ord('라'), ord('ㅁ'): ord('마'), ord('ㅂ'): ord('바'), ord('ㅃ'): ord('빠')}
                cho = d.get(cho)
            else:
                cho = (cho - 12604) * 588 + 44032
            dictionaries = SDictionary.objects.filter(pk=0)
            for i in range(588):
                dictionary = SDictionary.objects.filter(name__istartswith=chr(cho + i))
                dictionaries = dictionaries | dictionary
            serializer = SDictionarySerializer(dictionaries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': '초성이 아닙니다.'
            }, status=status.HTTP_400_BAD_REQUEST)