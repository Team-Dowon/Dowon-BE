from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from dowonpackage.tag import Okt


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


import torch
from torch import nn
from torch.utils.data import Dataset
import gluonnlp as nlp
import numpy as np

# kobert
from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model

# BERT 모델, Vocabulary 불러오기 필수
bertmodel, vocab = get_pytorch_kobert_model()


# KoBERT에 입력될 데이터셋 정리
class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len,
                 pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i],))

    def __len__(self):
        return (len(self.labels))

    # 모델 정의


class BERTClassifier(nn.Module):  ## 클래스를 상속
    def __init__(self,
                 bert,
                 hidden_size=768,
                 num_classes=6,  ##클래스 수 조정##
                 dr_rate=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size, num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        _, pooler = self.bert(input_ids=token_ids, token_type_ids=segment_ids.long(),
                              attention_mask=attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        return self.classifier(out)


# Setting parameters
max_len = 64
batch_size = 32
warmup_ratio = 0.1
num_epochs = 20
max_grad_norm = 1
log_interval = 100
learning_rate = 5e-5

device = torch.device('cpu')
model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)
model.load_state_dict(
    torch.load('./SentimentAnalysisKOBert_StateDict.pt', map_location='cpu'))

# 토큰화
tokenizer = get_tokenizer()
tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)


def new_softmax(a):
    c = np.max(a)  # 최댓값
    exp_a = np.exp(a - c)  # 각각의 원소에 최댓값을 뺀 값에 exp를 취한다. (이를 통해 overflow 방지)
    sum_exp_a = np.sum(exp_a)
    y = (exp_a / sum_exp_a) * 100
    return np.round(y, 3)


# 예측 모델 설정
def predict(predict_sentence):
    data = [predict_sentence, '0']
    dataset_another = [data]

    another_test = BERTDataset(dataset_another, 0, 1, tok, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=5)

    model.eval()

    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length = valid_length

        out = model(token_ids, valid_length, segment_ids)

        for i in out:
            logits = i
            logits = logits.detach().cpu().numpy()
            probability = []
            logits = np.round(new_softmax(logits), 3).tolist()
            for logit in logits:
                probability.append(np.round(logit, 3))

            if np.argmax(logits) == 0:
                emotion = "기쁨"
            elif np.argmax(logits) == 1:
                emotion = "불안"
            elif np.argmax(logits) == 2:
                emotion = '당황'
            elif np.argmax(logits) == 3:
                emotion = '슬픔'
            elif np.argmax(logits) == 4:
                emotion = '분노'
            elif np.argmax(logits) == 5:
                emotion = '상처'

            probability.append(emotion)
    return probability


# 사용자 정보
class test(APIView):
    def post(self, request):
        sentence = request.data['sentence']
        s_predict = predict(sentence)
        emotion = s_predict[6]
        s_predict.pop()
        percent = max(s_predict)

        return JsonResponse({'예측값': emotion, '확률': percent}, status=200)