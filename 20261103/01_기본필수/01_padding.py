import torch
from torch import nn
torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
                          # torch.set_num_threads() 함수로 PyTorch가 내부 연산(CPU 멀티스레딩)에 사용할 스레드의 개수를 제한합니다.
                          # 성능 벤치마크나 일관된 타이밍 테스트를 할 때 자원 격리를 위해 주로 사용됩니다.
torch.manual_seed(42)

from torch.nn.utils.rnn import pad_sequence # 입력 리스트에 포함된 텐서들 중 가장 긴 첫번째 축의 길이는 sequence[2]의 5 입니다.
                                            # pad_sequence(..., batch_first=) 함수에서 batch_first=True 이므로 배치가 맨 앞으로 옵니다.
                                            # (전체 자료의 개수, 가장 긴 시퀀스 길이, 나머지 고정 차원)의 결과 형태에 따라 (3, 5, 3) 구조의 3차원 텐서가 생성됩니다.
# 서로 길이가 다른 3개 자료. 각 시점의 특성 수는 3개이다.
sequences = [torch.ones(4,3), torch.ones(2,3)*2, torch.ones(5,3)*3] # sequences[0]: torch.ones(4, 3) -> 크기 (4, 3)인 1로 채워진 텐서
                                                                    # sequences[1]: torch.ones(2, 3) * 2 -> 크기 (2, 3)인 2로 채워진 텐서
                                                                    # sequences[2]: torch.ones(5, 3) * 3 -> 크기 (3, 3)인 3으로 채워진 텐서
                                                                    # 각 자료는 첫 번째 축(행)의 길이(4, 2, 5)가 서로 다른 가변 길이 시퀀스이며, 두 번째 축(열)의 크기는 3으로 고정되어 있습니다.
# TODO B01: B가 첫 축인 [3,5,3] Padding Tensor를 만든다.
# batch_first의 기본값은 False이다. 여기서는 True로 바꾼다.
# BEGIN B01
padded = pad_sequence(sequences, batch_first=True) # 원본 데이터 sequence[1]은 원래(2, 3) 크기의 2. 으로 가득 찬 행렬이었습니다.
                                                   # 하지만 최고 길이인 5에 맞춰야 하므로, 부족한 하단 3개 행에 원소 값이 0. 으로 Padding(패딩된 채워넣기)이 수행됩니다.
                                                   # 이 때문에 출력 결과가 2. 으로 구성된 2개 행과 0. 으로 구성된 3개 행으로 합쳐저 (5, 3) 크기로 나타납니다.
# END B01
print("입력 길이:", [len(x) for x in sequences])
print("Padding shape:", tuple(padded.shape))
print("두 번째 자료:\n", padded[1])
