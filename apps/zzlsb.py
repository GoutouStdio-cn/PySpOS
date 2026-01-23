#   
#   zzlsb.py
#   简单的猜数字游戏（别问我为什么文件名是zzlsb）
#
#   2026/1/23 by GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import random

number = 0   # 初始化这个数字为0
text = ['炸鸡', '炖肉', '胖牛', '汉堡', '飞电6Chanllger'] # 语库列表

def main():
    print("简单猜数字游戏，根据提示语找答案！\n")
    number = random.randint(0,100)  # 生成答案
    dmm = random.randint(0,6)       # 大妈妈
    print(f"大妈妈，你要做{text[dmm]}的话，你大该要放{float(number / dmm)}克盐。\n\n")

    while True:
        ip = int(input("输入你猜的数字："))

        if ip == number:
            print("恭喜你猜中了！\n")
            break
        else:
            print(f"很遗憾你没有猜中，答案是{number}\n")

if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")