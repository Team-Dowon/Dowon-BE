from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from dowonpackage.tag import Okt
from api.kobert_predict import bert_predict

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


# 사용자 정보
class test(APIView):
    def post(self, request):
        try:
            sentence = request.data['sentence'] # sentence 데이터 가져오기
            s_predict = bert_predict(sentence)  # sentence 데이터 넣기
            v_predict = s_predict.area()    # sentence 데이터로 감성 예측
            emotion = v_predict[6]
            v_predict.pop()
            percent = max(v_predict) # 최고 확률 값 확인

            return JsonResponse({'예측값': emotion, '확률': percent}, status=200)    # 프론트로 전달
        except Exception as e:  # 에러 값 확인
            return Response({
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
