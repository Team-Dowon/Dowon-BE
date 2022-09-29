from konlpy.tag import Okt
okt = Okt()

# 입력할 문장
text = "이 치킨 진짜 겉바속촉 미쳤다 ㅠㅠ 진짜 피꺼솟 겉바속촉"

#text에서 형태소 반환
morphs=okt.morphs(text)
print(morphs)

# 신조어 목록 텍스트 파일 읽어오기
textFile = open("ListSlang.txt",'r',encoding='UTF8')

# 신조어들 배열로 받을 빈 배열 생성
slanglist = []

# ListSlang.txt에 적혀있는 신조어들 slanglist배열에 한 단어씩 append
while True:
    slang = textFile.readline()
    if not slang:
        break
    slanglist.append(slang.strip())

# 반환된 형태소들 중 신조어 목록에 있는 단어와 일치하는 단어가 있으면 출력
for extraction in morphs:
    if str(extraction) in slanglist:
        print(str(extraction))

# text에 적힌 문장 속 신조어들 이해하기 쉽게 변환
print(okt.normalize(text))

textFile.close()

# text에서 명사를 반환
# nouns=okt.nouns(text)
# print(nouns)

# text에서 품사 정보 부착하여 반환
# print(okt.pos(text))
