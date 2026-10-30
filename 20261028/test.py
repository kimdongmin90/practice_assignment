# print(10 == 100)
# print(10 != 100)
# print(10 < 100)
# print(10 > 100)
# print(10 <= 100)
# print(10 >= 100)

# print("가방" == "가방")
# print("가방" != "하마")
# print("가방" < "하마")
# print("가방" > "하마")

# x = 25
# print(10 < x < 30)
# print(40 < x < 60)

# print(not True)
# print(not False)

# x = 10
# under_20 = x < 20
# print("under_20:", under_20)
# print("not under_20:", not under_20)

# print(True and True)
# print(True and False)
# print(False and True)
# print(False and False)
# print(True or True)
# print(True or False)
# print(False or True)
# print(False or False)

# if True:
#     print("True입니다...")
#     print("정말 True입니다...")

# "True입니다..."
# "정말 True입니다..."

# if False:
#     print("False입니다...!")

# number = input("정수 입력> ")
# number = int(number)

# if number > 0:
#     print("양수입니다")

# if number < 0:
#     print("음수입니다")

# if number == 0:
#     print("0입니다")

# import datetime

# now = datetime.datetime.now()

# print(now.year, "년")
# print(now.month, "월")
# print(now.day, "일")
# print(now.hour, "시")
# print(now.minute, "분")
# print(now.second, "초")

# import datetime

# now = datetime.datetime.now()

# print("{}년 {}월 {}일 {}시 {}분 {}초".format(
#     now.year,
#     now.month,
#     now.day,
#     now.hour,
#     now.minute,
#     now.second
# ))

# import datetime

# now = datetime.datetime.now()

# if now.hour < 12:
#     print("현재 시각은 {}시로 오전입니다!".format(now.hour))

# else:
#     print("현재 시각은 {}시로 오후입니다!".format(now.hour))

# if now.hour >= 12:
#     print("현재 시각은 {}시로 오후입니다!".format(now.hour))

# import datetime

# now = datetime.datetime.now()

# if 3 <= now.month <= 5:
#     print("이번 달은 {}월로 봄입니다!".format(now.month))

# elif 6 <= now.month <= 8:
#     print("이번 달은 {}월로 여름입니다!".format(now.month))

# elif 9 <= now.month <= 11:
#     print("이번 달은 {}월로 가을입니다!".format(now.month))

# else:
#     print("이번 달은 {}월로 겨울입니다!".format(now.month))

# number = input("정수 입력> ")
# number = int(number)

# if number % 2 == 0:
#     print("짝수입니다")

# if number % 2 == 1:
#     print("홀수입니다")

# last_character = number[-1]

# last_number = int(last_character)

# if last_number == 0 \
#     or last_number == 2 \
#     or last_number == 4 \
#     or last_number == 6 \
#     or last_number == 8:
#     print("짝수입니다")

# if last_number == 1 \
#     or last_number == 3 \
#     or last_number == 5 \
#     or last_number == 7 \
#     or last_number == 9:
#     print("홀수입니다")

# if last_character in "02468":
#     print("짝수입니다")

# if last_character in "13579":
#     print("홀수입니다")

# a = float(input("> 1번째 숫자: "))
# b = float(input("> 2번째 숫자: "))
# print()

# if a > b:
#     print("처음 입력했던 {}가 {}보다 더 큽니다".format(a, b))

# if a < b:
#     print("두 번째로 입력했던 {}가 {}보다 더 큽니다".format(b, a))