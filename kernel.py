# kernel.py - PySpOS 内核处理(不是真内核)

import printk
import os
import sys
import subprocess
import main
import time
import shutil
from fs import current_dir
import uuid
import hashlib
import random

# PySpOS ASCII 艺术 Logo   
ascii_logo = r'''
 ____            ____             ___    ____      _____
|  _ \   _   _  / ___|   _ __    / _ \  / ___|    |___ / 
| |_) | | | | | \___ \  | '_ \  | | | | \___ \      |_ \ 
|  __/  | |_| |  ___) | | |_) | | |_| |  ___) |    ___) |
|_|      \__, | |____/  | .__/   \___/  |____/    |____/ 
         |___/          |_|           

PySpOS 模拟操作系统 版本 3
@ 2022~2025 GoutouStdio（或狗头工作室）保留所有权利。                   
'''

# 逻辑核心计数
cores = os.cpu_count()

# 获取系统用户名
def get_system_username() -> str:
    username = os.getenv("USER") or os.getenv("USERNAME")
    if username and username.strip():
        return username.strip()

    try:
        username = os.getlogin()
        if username.strip():
            return username.strip()
    except OSError:
        pass

    try:
        result = subprocess.check_output(
            ["whoami"],
            encoding="utf-8",
            stderr=subprocess.DEVNULL
        ).strip()
        if sys.platform == "win32":
            username = result.split("\\")[-1]
        else:
            username = result
        if username.strip():
            return username.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass

    if sys.platform.startswith("linux") or sys.platform == "darwin":
        try:
            import pwd
            username = pwd.getpwuid(os.getuid()).pw_name
            return username.strip()
        except (ImportError, ModuleNotFoundError):
            pass
    elif sys.platform == "win32":
        # 通过 pywin32 获取
        try:
            import win32api
            username = win32api.GetUserName()
            return username.strip()
        except (ImportError, ModuleNotFoundError):
            pass

    # 所有方法均失败
    raise RuntimeError("无法获取用户名")

# 生成Unlock Token
def generate_token():
    # 基础信息
    base_info = f"{uuid.getnode()}-{random.randint(1000,9999)}-unlock_token-{get_system_username()}" # 格式为 设备ID--1000~9999随机数-unlock_token-用户名
    # 生成SHA256哈希作为token
    token = hashlib.sha256(base_info.encode('utf-8')).hexdigest()
    return token

# unlock token
token = generate_token()

# Y\N 确认提示
def confirm(prompt: str) -> bool:
    while True:
        # 拼接提示信息，末尾添加 [y/n]
        user_input = input(f"{prompt} [y/n]: ").strip().lower()
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            # 无效输入时提示重新输入
            print(f"\033[33m无效输入：{user_input}，请输入 y 或 n\033[0m")



# 打印提示符
def print_prompt():
    # 获取当前目录名称
    current_dir_name = os.path.basename(current_dir)
    username = get_system_username()
    # 获取格式化的当前时间
    current_time = time.strftime("%H:%M:%S")

    # 基础设置
    if main.rootstate or main.bootcfg.get('rootstate', False):
        # ROOT用户
        prompt_header = (
            f"┌──\033[91m({username}@PySPOS)─[ROOT]─[\033[93m{current_time}\033[91m]─(\033[94m/%s\033[91m)\033[0m"
            % current_dir_name
        )
        prompt_line = f"└─\033[91m\033[94m#\033[0m "  # ROOT用#号
    else:
        # 用户
        prompt_header = (
            f"┌──\033[92m({username}@PySPOS)─[\033[93m{current_time}\033[92m]─(\033[94m/%s\033[92m)\033[0m"
            % current_dir_name
        )
        prompt_line = f"└─\033[92m\033[94m$\033[0m "

    # 双行显示提示符
    print(prompt_header)
    return prompt_line

# 内核主循环
def loop():    
    username = get_system_username()
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")    
    print(ascii_logo)

    print(f"\n你有 {cores} 个 CPU 逻辑核心，Token = {token}")
    print(f"欢迎使用 PySpOS 操作系统，{username}！")
    print()  # 打印一个空行
    while 1:
        try:
            prompt = input(print_prompt())
            
            main.handle_command(prompt)

        except Exception as e:
            printk.error(f"{e}")

# 退出PySpOS
def exit():
    if os.path.isdir("__pycache__"):
        try:
            shutil.rmtree("__pycache__")
            shutil.rmtree("apps/__pycache__")
            printk.ok("已删除缓存目录 __pycache__")
        except Exception as e:
            printk.error(f"无法删除缓存目录: {e}")
    else:
        printk.warn("未找到缓存目录 __pycache__，无需删除")
    
    if os.path.isdir("%s/apps/__pycache__" % current_dir):
        try:
            shutil.rmtree("%s/apps/__pycache__" % current_dir)
            printk.ok("已删除软件缓存目录 apps/__pycache__")
        except Exception as e:
            printk.error(f"无法删除缓存目录: {e}")
    else:
        printk.warn("pass...")
    printk.info("正在关闭 PySpOS 操作系统...")
    time.sleep(1)
    sys.exit(0)