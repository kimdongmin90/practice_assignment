"""실습 01 · RGB 이미지의 N,C,H,W를 확인한다. 실제 사진 대신 정상 Tensor 4장."""
import torch # 딥러닝 연산, 텐서(Tensor) 생성 및 관리의 핵심 패키지인 파이토치 라이브러리를 불러옵니다.

torch.manual_seed(42) # torch.manual_seed() 함수를 이용해 난수를 생성하는 알고리즘의 시작값을 고정합니다.
                      # 코드를 몇번 다시 실행해도 torch.rand()가 만들어내는 난수의 패턴이 항상 똑같이 유지되도록 하여 실험의 재현성(Reproducibility)을 확보합니다.
# 해설 B01: rand의 네 크기는 이미지 수, 채널, 높이, 너비이다.
# 필수: 각 차원의 크기. 선택: dtype, device. 기본 float32·CPU를 사용한다.
# BEGIN B01
# TODO B01: RGB 이미지 4장, 높이·너비 32인 Tensor를 만든다.
images = torch.rand(4, 3, 32, 32) # 텐서의 형태 분석(딥러닝 표준 이미지 배치 포맷)
                                  # 첫번째 차원: Batch Size(배치 크기) -> 이미지 4장을 한 묶음(Batch)으로 가집니다.
                                  # 두번째 차원: Channel(채널 수) -> 컬러 이미지의 기본인 RGB 3개 채널(Red, Green, Blue)을 의미합니다.
                                  # 세번째 차원: Height(이미지 높이) -> 세로 픽셀 수(px)입니다.
                                  # 네번째 차원: Width(이미지 너비) -> 가로 픽셀 수(px)입니다.
# END B01
print("shape:", tuple(images.shape)) # .shape 명령어로 속성을 통해 텐서가 가진 갖ㅈ 차원의 크기를 확인하고, 이를 파이썬 튜플 형태로 변환해 출력합니다.
print("dtype:", images.dtype) # .dtype 명령어로 속성을 통해 내부 원소들의 데이터 타입(Data Type)을 출력합니다.
                              # torch.rand() 함수는 기본적으로 32비트 부동소수점 실수형인 torch.float32(줄여서 float)를 사용합니다.
print("device:", images.device) # .device 명령어로 속성을 통해 해당 텐서가 어느 하드웨어 메모리에 올라가 있는지 출력합니다.
                                # 별도로 GPU(.cuda())로 보내는 명령을 하지 않았으므로, 기본값인 CPU가 출력됩니다.
print("첫 이미지:", tuple(images[0].shape)) # images[0]은 배치 4장 중 첫번째 이미지에 해당하며, 슬라이싱 결과로(3, 32, 32) 크기의 3차원 텐서가 됩니다.
                                           # .shape을 구하고 튜플로 변환하여 출력합니다.