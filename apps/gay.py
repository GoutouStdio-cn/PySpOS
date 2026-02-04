import string
import time

text = "Hello world Chen Yang is gay"

def main():
    temp = ""
    for ch in text:
        for i in string.printable:
            if i == ch or ch == " ":
                time.sleep(0.01)
                print(temp + i)
                temp += ch
                break
            else:
                time.sleep(0.01)
                print(temp + i)
    print() # 打印空行
    
if __name__ == "__exec__":
    main()
