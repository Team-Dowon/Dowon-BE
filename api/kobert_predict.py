from torch.utils.data import Dataset
from kobert.pytorch_kobert import get_pytorch_kobert_model
from kobert.utils import get_tokenizer
# torch
import torch
from torch import nn
import gluonnlp as nlp
import numpy as np
from torch.utils.data import Dataset


# KoBERT에 입력될 데이터셋 정리
class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len,
                 pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return self.sentences[i] + (self.labels[i],)

    def __len__(self):
        return len(self.labels)


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


class BertModel():
    # BERT 모델, Vocabulary 불러오기 필수
    bertmodel, vocab = get_pytorch_kobert_model()

    device = torch.device('cpu')
    model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)
    model.load_state_dict(
        torch.load('/root/model/SentimentAnalysisKOBert_StateDict.pt', map_location='cpu'))


class bert_predict(object):
    def __init__(self, predict_sentence):
        self.predict_sentence = predict_sentence

    def new_softmax(logits):
        c = np.max(logits)  # 최댓값
        exp_a = np.exp(logits - c)  # 각각의 원소에 최댓값을 뺀 값에 exp를 취한다. (이를 통해 overflow 방지)
        sum_exp_a = np.sum(exp_a)
        y = (exp_a / sum_exp_a) * 100
        return np.round(y, 3)


    # 예측 모델 설정
    def area(self):
        vocab = BertModel.vocab

        # Setting parameters
        max_len = 64
        batch_size = 32

        # 토큰화
        tokenizer = get_tokenizer()
        tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
        device = torch.device("cpu")

        data = [self.predict_sentence, '0']
        dataset_another = [data]

        another_test = BERTDataset(dataset_another, 0, 1, tok, max_len, True, False)
        test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=5)

        BertModel.model.eval()

        for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
            token_ids = token_ids.long().to(device)
            segment_ids = segment_ids.long().to(device)

            valid_length = valid_length

            out = BertModel.model(token_ids, valid_length, segment_ids)

            for i in out:
                logits = i
                logits = logits.detach().cpu().numpy()
                probability = []
                c = np.max(logits)  # 최댓값
                exp_a = np.exp(logits - c)  # 각각의 원소에 최댓값을 뺀 값에 exp를 취한다. (이를 통해 overflow 방지)
                sum_exp_a = np.sum(exp_a)
                y = (exp_a / sum_exp_a) * 100
                x = np.round(y, 3)
                logits = np.round(x, 3).tolist()
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