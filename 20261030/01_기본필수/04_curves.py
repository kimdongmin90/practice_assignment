from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다.
import matplotlib.pyplot as plt

# 아래 20개 값은 학습곡선 읽기용으로 제공한 설명용 값입니다.
# 실제 모델 실행 결과라고 보고하지 않습니다. 07번은 직접 학습한 곡선을 그립니다.
train_losses = [0.90,0.76,0.65,0.56,0.49,0.43,0.38,0.33,0.29,0.25,
                0.22,0.20,0.18,0.16,0.14,0.13,0.12,0.11,0.10,0.09]
valid_losses = [0.94,0.81,0.71,0.61,0.53,0.47,0.42,0.38,0.35,0.33,
                0.32,0.33,0.35,0.37,0.40,0.43,0.46,0.48,0.50,0.52]
# valid_losses에서 가장 작은 값의 위치를 구하고 1을 더해 best_epoch에 넣으세요.
# 리스트 위치는 0부터, 여기서 출력할 epoch는 1부터 시작합니다.
# >>> B05
# TODO B05: 위 요구사항에 맞게 이 블록만 완성합니다.
best_epoch = valid_losses.index(min(valid_losses)) + 1 # valid_loss가 낮을수록 완벽하게 맞췄다는 뜻이므로, min()함수를 통해 가장 작은 숫자가 얼마인지 파악합니다.
                                                       # .index() 함수로 최저 점수를 기록한 데이터가 리스트의 몇 번째 칸(Index)에 있는지 거꾸로 추적합니다.
                                                       # 숫자를 컴퓨터는 0부터 세고, 사람은 1부터 세기 때문에 발생하는 오차 보정을 위해 1을 더해줍니다.
                                                       # 파이썬 내장 함수인 min() 함수로 valid_losses 리스트 안의 소수점 20개를 훑어보고 가장작은 숫자인 0.32를 대표값으로 뽑아내어 valid_losses.index(0.32) + 1 상태가 됩니다.
                                                       # 컴퓨터는 첫번째 데이터를 0, 두번째 데이터를 1 .... 이렇게 세어가므로 리스트에서 0.32는 11번째 위치하고 있기 때문에 번호는 10이 됩니다.
                                                       # 10번째라는 번호에 보정값 1을 더해주면 best_epoch에 11이 저장됩니다.

# <<< B05
print("best epoch:", best_epoch, "최소 valid loss:", min(valid_losses))
plt.figure(figsize=(8, 5))
plt.plot(range(1, 21), train_losses, label="train")
plt.plot(range(1, 21), valid_losses, label="valid")
plt.axvline(best_epoch, linestyle="--", label="best epoch")
plt.xlabel("Epoch")
plt.ylabel("Cross entropy loss")
plt.legend()
plt.tight_layout()
plt.savefig(Path(__file__).resolve().parent / "practice04_curves.png", dpi=150)
plt.close()
print("생성: practice04_curves.png")
