from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import re
import json
from dowonpackage.tag import Okt
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import pickle
import keras


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