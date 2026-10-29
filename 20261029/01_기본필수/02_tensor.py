"""실습 02: 값뿐 아니라 shape·dtype·device를 같이 확인합니다."""
import torch
scalar = torch.tensor(3.0) # 0차원 텐서(0D Tensor)로 대괄호 없이 단 하나의 실수(소수점) 값인 3.0만 들어있습니다.
                           # shape을 측정하면 아무것도 없는 빈 값(torch.Size([]))이 나옵니다.
                           # 인공지능 모델이 최종적으로 '최종 손실률 점수(Loss value)'나 오차 수치, 단일 상수 값을 저장할 때 주로 이 형태로 다룹니다.
vector = torch.tensor([1.0, 2.0, 3.0]) # 1차원 텐서(1D Tensor)로 파이썬 리스트 구조를 뜻하는 대괄호[...] 안에 여러 개의 숫자가 한 줄로 나열되어 있습니다.
                                       # 3개의 숫자가 한 방향으로 나열되어 있으므로 shape은 torch.Size([3])이 됩니다.
                                       # 텍스트 데이터의 단어 임베딩 벡터, 혹은 이미지의 특정 특징들을 일렬로 쭉 펼쳐놓은 특징 벡터(Feature vector) 배열을 다룰 때 이 형태로 진입합니다.
# [[1.0, 2.0], [3.0, 4.0]]을 torch.float32의 2차원 Tensor matrix로 만드세요.
# 자료를 CPU로 옮기는 코드는 제공되어 있습니다.
# >>> B02
# TODO B02: 위 요구사항을 읽고 이 블록을 완성하세요.
matrix = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32) # sclar: 방향 없이 값만 있는 0차원 점입니다.
                                                                     # vector: 숫자들이한 줄로 나열된 1차원 선입니다.
                                                                     # matrix: 행(Row)과 열(Column)을 갖추어 면적을 가지는 2차원 평면 구조입니다.
                                                                     # 이미지나 표 데이터를 다루기 위해 대괄호를 두번 감싸서([[...]]) 행렬 형태로 접근합니다.
# <<< B02
matrix = matrix.to("cpu") # matrix 텐서 저장 장치를 CPU 메모리 영역으로 강제 이동(정확히는 복사)합니다.
                          # 만약 이 행렬이 GPU 환경에서 수행 중이었다면, 이 코드를 거친 후 안전하게 CPU 장치로 안착하여 일반 파이썬 기능들과 연동할 수 있는 상태가 됩니다.
print("스칼라:", tuple(scalar.shape), scalar.dtype, scalar.device) # 출력 예측 -> 스칼라: () torch.float32 cpu
                                                                  # 0차원 점 데이터이므로 모양은 빈 튜플()로 나오고, 소수점 규격과 현재 장치 위치가 찍힙니다.
print("벡터:", tuple(vector.shape), vector.dtype, vector.device) # 출력 예측 -> 벡터: (3,) torch.float32 cpu
                                                                # 1차원 선 데이터이므로 3개의 방을 가진 구조인 (3,) 모양이 출력됩니다.
print("행렬:", tuple(matrix.shape), matrix.dtype, matrix.device) # 출력 예측 -> 행렬: (2, 2) torch.float32 cpu
                                                                # 앞서 정의한 2행 2열짜리 표 구조가 (2,2) 형태로 변환되어 출력됩니다.
print("행렬 값:", matrix.tolist()) # 출력 예측 -> 행렬 값: [[1.0, 2.0], [3.0, 4.0]]
                                  # 화면에 tensor([[1., 2.], ...]) 같은 파이토치 전용 글자가 붙어 나오는 대신, 순수한 파이썬 2차원 리스트 양식으로 알맹이 값만 깔끔하게 출력해 줍니다.
