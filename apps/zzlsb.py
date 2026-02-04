#   
#   zzlsb.py
#   简单的猜数字游戏（别问我为什么文件名是zzlsb）
#
#   2026/1/23 by GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import random

FOOD_OPTIONS = ['', '炸鸡', '炖肉', '胖牛', '汉堡', '飞电6Chanllger']

def main():
    print("简单猜数字游戏，根据提示语找答案！\n")
    secret_number = random.randint(0, 100)
    food_index = random.randint(1, 6)
    print(f"大妈妈，你要做{FOOD_OPTIONS[food_index]}的话，你大该要放{float(secret_number / food_index)}克盐。\n\n")

    while True:
        try:
            user_guess = int(input("输入你猜的数字："))

            if user_guess == secret_number:
                print("恭喜你猜中了！\n")
                break
            elif user_guess < secret_number:
                print("猜小了，再试试！\n")
            else:
                print("猜大了，再试试！\n")
        except ValueError:
            print("请输入有效的数字！\n")
        except Exception as e:
            print(f"发生了未知错误：{e}\n")

if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")