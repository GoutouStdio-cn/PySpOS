#!/usr/bin/env python3
#  
#   launcher.py
#   PySpOS 启动器
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import os
import sys
import time

def get_boot_time():
    return time.time()

def main():
    boot_time = get_boot_time()
    
    try:
        import logk
    except ImportError:
        class logk:
            @staticmethod
            def printl(module, message, boot_time):
                elapsed = time.time() - boot_time
                print(f"[{elapsed:10.6f}] {module}: {message}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = script_dir
    
    logk.printl("launcher", "PySpOS launcher", boot_time)
    logk.printl("launcher", f"根目录: {root_dir}", boot_time)
    
    current_slot_file = os.path.join(root_dir, "current_slot")
    current_slot = None
    slot_path = None
    use_slot = False
    
    if os.path.exists(current_slot_file):
        try:
            with open(current_slot_file, 'r') as f:
                current_slot = f.read().strip()
                slot_path = os.path.join(root_dir, current_slot)
                logk.printl("launcher", f"当前槽位: {current_slot}", boot_time)
                
                main_py = os.path.join(slot_path, "main.py")
                if os.path.exists(main_py):
                    print(f"\n[launcher] 检测到槽位 {current_slot}，是否从槽位启动？(y/n): ", end='', flush=True)
                    try:
                        user_input = input().strip().lower()
                        if user_input == 'y' or user_input == 'yes':
                            use_slot = True
                            logk.printl("launcher", "用户选择从槽位加载系统文件", boot_time)
                        else:
                            logk.printl("launcher", "用户选择从src目录加载系统文件", boot_time)
                    except (EOFError, KeyboardInterrupt):
                        print("n")
                        logk.printl("launcher", "非交互式环境，默认从src目录加载系统文件", boot_time)
                else:
                    logk.printl("launcher", "槽位无效，将从src目录加载系统文件", boot_time)
        except Exception as e:
            logk.printl("launcher", f"读取槽位文件失败: {e}，将从src目录加载系统文件", boot_time)
    else:
        logk.printl("launcher", "未找到槽位文件，将从src目录加载系统文件", boot_time)
    
    if use_slot:
        system_path = slot_path
        logk.printl("launcher", f"从槽位加载系统文件: {system_path}", boot_time)
    else:
        system_path = os.path.join(root_dir, "src")
        logk.printl("launcher", f"从src目录加载系统文件: {system_path}", boot_time)
    
    main_py = os.path.join(system_path, "main.py")
    if not os.path.exists(main_py):
        logk.printl("launcher", f"错误: 找不到 main.py: {main_py}", boot_time)
        logk.printl("launcher", "系统文件不完整，无法启动", boot_time)
        sys.exit(1)
    
    if system_path not in sys.path:
        sys.path.insert(0, system_path)
    
    apps_path = os.path.join(system_path, "apps")
    if os.path.exists(apps_path) and apps_path not in sys.path:
        sys.path.insert(0, apps_path)
    
    os.chdir(system_path)
    logk.printl("launcher", f"工作目录: {os.getcwd()}", boot_time)
    
    sys._launcher_detected = True
    
    try:
        logk.printl("launcher", "启动热重启环境...", boot_time)
        import hotreset_env
        hotreset_env.run()
    except Exception as e:
        logk.printl("launcher", f"启动失败: {e}", boot_time)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()