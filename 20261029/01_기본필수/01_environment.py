"""실습 01: 설치된 PyTorch와 CUDA 노출을 확인합니다. GPU가 없어도 CPU로 진행합니다."""
import torch

print("PyTorch:", torch.__version__) # torch.__version__ 명령을 통해 내 컴퓨터에 설치된 파이토치 프로그램의 버전을 알아봅니다.
print("PyTorch CUDA 빌드:", torch.version.cuda)
print("CUDA 사용 가능:", torch.cuda.is_available()) # torch.version.cuda / is_available() 명령을 통해 인공지능 고속 계산 기술인 'CUDA(쿠다)'가 내 컴퓨터에서 켜질 수 있는지 확인합니다.
                                                   # 가능하다면 True(예), 안 된다면 False(아니오)라고 대답합니다.
# GPU 함수는 사용 가능한 경우에만 호출합니다. 드라이버 번호는 터미널 nvidia-smi에서 별도로 기록합니다.
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0)) # GPU를 쓸 수 있다면, 그래픽카드의 진짜 이름(예: NVIDIA GeForce RTX 5080)을 화면에 출력합니다.
    print("VRAM GiB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)) # 인공지능이 데이터를 올려 놓고 학습할 작업대 크기인 비디오 메모리(VRAM)용량을 GiB 단위로 계산해서 소수점 둘째 자리까지 round해서 출력합니다.
else:
    print("GPU: 이번 실행에서는 사용하지 않음")
print("이 단계의 연산 장치: cpu")
# 정상 숫자 1.0, 2.0을 담은 Tensor를 sample에 저장하세요.
# 아래 덧셈 결과가 [2.0, 3.0]이면 계산 환경이 준비된 것입니다.
# >>> B01
# TODO B01: 위 요구사항을 읽고 이 블록을 완성하세요.
sample = torch.tensor([1.0, 2.0]) # 파이썬의 평범한 숫자 리스트인 [1.0, 2.0]으로 변경하고 파이토치 전용 고속 연산 박스(텐서)에 넣습니다.
# <<< B01
print("덧셈:", (sample + 1).tolist()) # 원래 파이썬 리스트에 + 1을 하면 에러가 나거나 먹통이 되지만, 파이토치 텐서는 박스 안에 든 모든 숫자에 동시에 1을 알아서 골고루 더해줍니다.(파이토치 박스의 장점)
                                     # .tolist() 함수를 통해 읽기 편한 파이썬 리스트 모양으로 바꿔서 출력해 줍니다.
