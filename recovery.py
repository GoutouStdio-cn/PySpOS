#
#   recovery.py
#   简易的模拟恢复模式
#
#   2026/1/23 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import main
import kernel
import logk
import shutil
import os
import gc

# 主程序
def recovery_main(jumpinfo) -> str:
    kernel.screen_clear() # 清屏
    logk.printl("recovery", f"跳入到recovery, jumpinfo={jumpinfo}", main.boot_time)
    logk.printl("recovery", "欢迎使用PySpOS Recovery，输入help获取可用命令", main.boot_time)
    while 1:
        prompt = input("recovery> ")    # 我们recovery的提示符

        if prompt == "help":
            print("help     打印本帮助信息")
            print("erase    清除bootcfg和pycache信息")
            print("optimize 清理Python运行内存，让性能更高（实验性的）")
            print("exit     退出Recovery\n")
        elif prompt == "erase":
            if os.path.isdir("etc"):
                shutil.rmtree("etc")
            else:
                logk.printl("recovery", "etc文件夹已经清除了", main.boot_time)
            
            if os.path.isdir("__pycache__"):
                shutil.rmtree("__pycache__")
            else:
                logk.printl("recovery", "pycache文件夹已经清除了", main.boot_time)
            logk.printl("recovery", "清除完成，请重启程序\n", main.boot_time)
        elif prompt == "exit":
            break
        elif prompt == "optimize":
            # 触发垃圾回收2次
            gc.collect()
            gc.collect(2)
            logk.printl("recovery", "已清理垃圾！\n", main.boot_time)
        else:
            print(f"找不到 {prompt} 命令")
    
    logk.printl("recovery", "Recovery已退出", main.boot_time)
    

