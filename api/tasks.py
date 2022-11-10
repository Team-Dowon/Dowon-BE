# tasks.py

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from api.kobert_predict import bert_predict

# test 용 함수
@shared_task
def bert_predict_c(sentence):
    s_predict = bert_predict(sentence)

    return s_predict