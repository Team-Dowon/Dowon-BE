# tasks.py

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from api.kobert_predict import bert_predict

# test 용 함수
@shared_task
def bert_predict_c(sentence):
    s_predict = bert_predict(sentence)
    v_predict = s_predict.area()  # sentence 데이터로 감성 예측
    emotion = v_predict[6]
    v_predict.pop()
    percent = max(v_predict)  # 최고 확률 값 확인
    return Response({'예측값': emotion, '확률': percent}, status=200)  # 프론트로 전달