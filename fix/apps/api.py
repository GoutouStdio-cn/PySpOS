# api.py - 提供给 apps 目录下应用程序调用的 API 接口
import os
import sys
from pathlib import Path

# 设置路径
current_directory = Path.cwd()
main_dir = current_directory.parent

syscall = os.path.join(main_dir)

sys.path.append(syscall)

# Import printk 和 kernel 和 main 模块
import printk
import kernel
import main

# API: 获取系统用户名
def get_system_username():
    return kernel.get_system_username()

# API: 进入内核主循环
def enter_kernel_loop():
    kernel.loop()

# API: 退出系统
def exit_system():
    kernel.exit()

# API: 打印信息
def api_info(message: str) -> None:
    printk.info(message)

# API: 打印不同级别的信息
def api_ok(message: str) -> None:
    printk.ok(message)

def api_error(message: str) -> None:
    printk.error(message)

def api_warn(message: str) -> None:
    printk.warn(message)

def api_print(message: str) -> None:
    print(message)

# API: 执行系统命令
def api_system(command: str) -> int:
    return os.system(command)

# API: 调整 rootstate 状态
def set_rootstate(state: bool) -> None:
    main.rootstate = state
