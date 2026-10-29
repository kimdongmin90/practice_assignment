"""실습 05: 정답 인덱스와 logits로 손실을 계산합니다."""
import torch
from torch import nn

logits = torch.tensor([[2.0, 0.0], [0.0, 2.0]]) # AI가각 보기를 얼마나 정답이라 생각하는지 내놓은 logits(원시 점수)을 정리합니다.
                                                # AI는 0번 보기에 2.0점, 1번 보기에 0.0점을 줬습니다.(0번이 정답이라 생각)
                                                # AI는 0번 보기에 0.0점, 1번 보기에 2.0점을 줬습니다.(1번이 정답이라 생각)
target = torch.tensor([0, 1], dtype=torch.long) # 컴퓨터가 채점할 수 있게 정답 번호를 컴퓨터용 정수 형식(torch.long)으로 지정합니다.
                                                # dtype = torch.long은 정답 번호처럼 소수점이 없는 정수를 파이토치에서 다룰 때 사용하는 전용 표준 규격입니다.
                                                # 1번 문제의 정답은 0번, 2번문제의 정답은 1번으로 인공지능 주장과 실제 정답이 일치한 상황입니다.
loss_fn = nn.CrossEntropyLoss() # CrossEntropyLoss() 함수를 이용하여 틀리면 벌점을 많이 주고 정답을 맞추면 벌점을 0에 가깝게 줍니다.
                                # loss_fn에 nn.CrossEntropyLoss()를 담아두고 loss_fn(logits, target)을 실행하여 AI가 낸 답안과 진짜 답안을 대조합니다.
# loss_fn에 logits와 target을 순서대로 넣어 loss를 계산하세요.
# logits에 softmax를 먼저 적용하지 마세요.
# >>> B05
# TODO B05: 위 요구사항을 읽고 이 블록을 완성하세요.
loss = loss_fn(logits, target) # loss_fn(logits, target)의 결과 자체가 이미 파이토치 텐서이므로, 맨 바깥의 torch.tensor(...)로 한번 더 감싸지 않고 보통 loss = loss_fn(logits, target)이라고 입력해도 작동합니다.
# <<< B05
print("logits:", tuple(logits.shape))
print("target:", tuple(target.shape), target.dtype)
print("loss:", round(loss.item(), 6))
