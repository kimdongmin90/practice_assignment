"""실습 01. 정답 박스 3개를 그립니다. 원본 scene.png는 바꾸지 않습니다."""
from pathlib import Path
import cv2
import pandas as pd
BASE = Path(__file__).resolve().parent
image = cv2.imread(str(BASE / "data/scene.png"))
boxes = pd.read_csv(BASE / "data/boxes_gt.csv")
result = image.copy()  # 그릴 배열을 복사하여 원본을 보존합니다.
for row in boxes.itertuples():
    # >>> B01
    # 요구: result에 (x1,y1)~(x2,y2) 박스를 두께 2로 그리세요.
    # cv2.rectangle의 이미지·두 점·색은 필수, thickness는 선택입니다.
    cv2.rectangle(result, (int(row.x1), int(row.y1)), (int(row.x2), int(row.y2)), (255, 0, 0), 2)  # TODO B01: 위 요구사항의 핵심 코드를 작성하세요.
                                                                                                   # 파일의 좌표는 연속 경계이고 화면 표시 때만 정수로 바꿉니다.
                                                                                                   # cv2.rectangle(): 이미지 위에 Bounding Box(사각형)를 그리는 함수
                                                                                                   # result : 사각형을 그릴 대상 이미지 (원본 배열이 직접 수정됨)
                                                                                                   # (int(row.x1), int(row.y1))
                                                                                                   #   → Bounding Box의 왼쪽 위 좌표 (x1, y1)
                                                                                                   # (int(row.x2), int(row.y2))
                                                                                                   #   → Bounding Box의 오른쪽 아래 좌표 (x2, y2)
                                                                                                   # int(): 픽셀 좌표는 정수로 전달해야 하므로 실수 좌표를 정수로 변환
                                                                                                   # (255, 0, 0): 사각형 테두리 색상
                                                                                                   #   → OpenCV는 BGR 순서를 사용하므로 파란색(Blue)
                                                                                                   # 2: 사각형 테두리 두께 (2픽셀)
                                                                                                   # 목적: 객체 탐지 결과의 위치를 이미지에 표시하여
                                                                                                   #       모델이 어떤 영역을 객체로 인식했는지 시각적으로 확인
    # <<< B01
    print("class:", row.class_id, "xyxy:", row.x1, row.y1, row.x2, row.y2, "GT confidence: N/A")
cv2.imwrite(str(BASE / "p01_boxes.png"), result)
print("shape:", image.shape, "저장: p01_boxes.png")
