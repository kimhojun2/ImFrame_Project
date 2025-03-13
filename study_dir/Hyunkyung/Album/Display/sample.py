#sample.py

from transformers import AutoTokenizer, AutoModelForPreTraining
from torch.nn.functional import softmax
import torch

# 토크나이저와 토큰 분류를 위한 모델 초기화
tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")
model = AutoModelForPreTraining.from_pretrained("monologg/koelectra-base-v3-discriminator")
# model.eval()

# 분석할 텍스트
text = "작년 강릉에서 찍은 사진 보여줘."
inputs = tokenizer(text, return_tensors="pt")

# 모델 예측 실행
with torch.no_grad():
    outputs = model(**inputs)
    predictions = softmax(outputs.logits, dim=-1)

# 예측 결과에서 키워드 추출
predicted_label_indices = predictions.argmax(-1)
labels = [model.config.id2label[label_id] for label_id in predicted_label_indices[0].tolist()]
keywords = [word for word, label in zip(tokenizer.tokenize(text), labels) if label != 'O']  # 'O'는 "Outside"를 의미, 키워드가 아닌 토큰

print(keywords)