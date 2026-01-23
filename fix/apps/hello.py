# hello.py - 一个简单的应用程序，打印问候信息

import api

count = 0

print(f"your username is: {api.get_system_username()}")

for _ in range(0, 5):
    api.api_print("Hello from apps/hello.py!(hello count: %d)" % count)
    count += 1