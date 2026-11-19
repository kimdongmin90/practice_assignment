"""실습 04. 무작위 초기화 YOLO26의 1 epoch 학습 연결 점검. 성능 실험이 아닙니다."""
from pathlib import Path
import yaml
import torch
from ultralytics import YOLO
BASE = Path(__file__).resolve().parent
# Windows에서도 읽기 worker가 스크립트를 재실행하지 않도록 진입점을 구분합니다.
if __name__ == "__main__":
    torch.set_num_threads(1)
    config = {"train": str(BASE/"data/images/train"), "val": str(BASE/"data/images/val"),
              "names": ["square", "circle", "triangle"]}
    config_path = BASE / "p04_dataset.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    model = YOLO("yolo26n.yaml")  # 구조만 생성합니다. COCO 사전학습 .pt와 다릅니다.
    # >>> B05
    # 요구: config_path로 1 epoch, imgsz=160, batch=4, CPU 학습을 호출하세요.
    # 나머지 옵션은 제공한 그대로 유지하세요. test 경로는 전달하지 않습니다.
    model.train(data=str(config_path), epochs=1, imgsz=160, batch=4, device="cpu")  # TODO B05: 위 요구사항의 핵심 코드를 작성하세요.
                                                                                    # model.train(...) 함수로 yolo26n.yaml로 초기화 된 뼈대 모델에 지정된 조건으로 가중치 학습을 시작하는 명령입니다.
                                                                                    # data=str() 함수로 위에서 생성한 config_path(p04_dataset.yaml) 설정 파일 경로를 지정합니다.
                                                                                    # 이 YAML 안에는 train 및 val 데이터의 위치와 name(클래스 이름) 정보가 포함되어 있어, 요구사항대로 test 경로 없이 데이터셋을 구성합니다.
                                                                                    # 요구사항에 명시된 대로 데이터셋 전체를 딱 1번만 순회(1 epoch)하도록 제한합니다.(기초 환경 테스트나 빠른 디버깅용 설정)
                                                                                    # 입력 이미지의 크기를 가로, 세로 160 픽셀 기반으로 리사이즈하여 학습하도록 지정합니다.
                                                                                    # 앞선 단계에서 다뤘던 이미지 규격(128 x 160)에 특화된 경량 학습 스케일입니다.
                                                                                    # 메모리에 한번에 올릴 데이터 샘플의 개수(Batch Size)를 4개로 지정합니다.
                                                                                    # GPU 하드웨어 가속 대신 시스템의 CPU 자원만을 사용하여 연산을 수행하도록 명시합니다.(torch.set_num_threads(1) 설정과 맞물려 과도한 멀티스레딩 오버헤드 없이 안정적으로 실행되도록 돕습니다.)
    # <<< B05
    print("task:", model.task, "names:", model.names, "device:", model.device)
    print("학습 결과:", BASE/"p04_runs/smoke")
