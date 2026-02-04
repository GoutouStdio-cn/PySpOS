# hello.py - 一个简单的应用程序，打印问候信息

import api

def main():
    print(f"your username is: {api.get_system_username()}")

    for i in range(5):
        api.api_print("Hello from apps/hello.py!(hello count: %d)" % i)

if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")