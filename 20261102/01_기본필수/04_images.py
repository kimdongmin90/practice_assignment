"""실습 04 · 필요한 하위 폴더는 ImageFolder의 이미지 저장 구조뿐이다."""
from pathlib import Path
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

root = Path(__file__).resolve().parent # 현재 실행중인 파이썬 스크립트 파일(__file__)의 절대 경로를 구한 뒤, 그 파일이 속한 디렉토리(부모 폴더)를 root 경로로 잡습니다.
                                       # 하드코딩된 절대 경로 대신 이 방법을 쓰면 프로젝트 폴더가 어디로 이동하든 코드가 깨지지 않고 안전하게 작동합니다.
# Resize(size)는 목표 크기가 필수. ToTensor()에는 필수 인자가 없다.
transform = transforms.Compose([transforms.Resize((32, 32)), transforms.ToTensor()]) # 이미지들을 모델에 넣기 전에 일관되게 가공하는 전처리 체인을 만듭니다.
                                                                                     # transforms.Resize((크기)) 함수로 폴더 안에 있는 이미지들의 원래 크기가 제각각이더라도 모두 크기(32 X 32)로 강제 리사이징합니다.(크기가 다르면 하나의 배치 텐서로 묶을 수 없기 때문입니다.)
                                                                                     # transforms.ToTensor() 함수로 이미지를 torch.Tensor(파이토치 텐서) 포맷으로 변환합니다.
                                                                                     # 픽셀 값의 범위가  [0, 255]에서 [0.0, 1.0] 사이의 실수형(float32)으로 자동 정규화되며, 축 순서도 일반 이미지 포맷(HWC)에서 파이트치 표준인 CHW로 바뀝니다.
# ImageFolder(root, transform=None): root는 필수, transform은 선택이다.
# BEGIN B04
# TODO B04: data/train을 주어진 transform으로 읽는다.
train = datasets.ImageFolder(root / "data" / "train", transform=transform) # 파이토치에서 Classification(분류) 데이터를 다룰 때 가장 많이 쓰는 강력한 클래스입니다.
                                                                           # 아래와 같은 표준 폴더 구조를 자동으로 인식합니다.
                                                                           # data/train/
                                                                           # ├── cat/  --> 자동으로 0번 라벨 부여
                                                                           # │   ├── img1.jpg
                                                                           # │   └── img2.jpg
                                                                           # └── dog/  --> 자동으로 1번 라벨 부여
                                                                           #     ├── img3.jpg
                                                                           #     └── img4.jpg
                                                                           # 클래스 이름(폴더명)을 알파벳 순서대로 정렬하여 자동으로 정수형 라벨(0, 1, 2 ...)을 매칭해줍니다.
                                                                           # 이 맵핑 관계는 train.class_to_idx 속성에 저장됩니다.
# END B04
loader = DataLoader(train, batch_size=4, shuffle=False, num_workers=0) # DataLoader() 함수로 전체 데이터셋에서 데이터를 한 장씩 꺼내오지 않고, 지정한 크기(batch_size=)만큼 묶어서 [N, C, H, W] 형태로 전달해줍니다.
                                                                       # shuffle=False 옵션으로 데이터를 섞지 않고 폴더 정렬 순서대로 가져옵니다.(학습 시 보통 True로 주어 데이터 순서를 섞지만, 확인할 때는 False로 설정)
images, labels = next(iter(loader)) # DataLoader를 반복자(Iterator)로 변환한 뒤, next()를 호출하여 가장 첫 번째 미니배치(이미지 4장, 라벨 4개)를 꺼내옵니다.
                                    # images.shape는 앞서 다룬(4, 3, 32, 32)가 되며, labels.shape는 각 이미지의 정답 라벨이 담긴 1차원 텐서(4,)가 됩니다.
print("학습 이미지:", len(train))
print("클래스:", train.class_to_idx)
print("배치:", tuple(images.shape), tuple(labels.shape))
print("라벨:", labels.tolist())
