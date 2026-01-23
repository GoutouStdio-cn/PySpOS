import api
import random

number = 0   # 初始化这个数字
def main():
    number = random.randint(0,100)

    print("大胖牛发放了%d个大粑粑" % number)
    while True:
        ip = int(input("输入你猜的数字> "))

        if ip == number:
            print("中")
            break
        else:
            print("没中")

if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")