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
    
    # 导入logk模块（用于日志输出）
    try:
        import logk
    except ImportError:
        # 如果logk不可用，使用print作为备选
        class logk:
            @staticmethod
            def printl(module, message, boot_time):
                print(f"[{boot_time:.6f}] {module}: {message}")
    
    # 获取启动器所在目录作为根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = script_dir
    
    logk.printl("launcher", "PySpOS launcher", boot_time)
    logk.printl("launcher", f"根目录: {root_dir}", boot_time)
    
    # 读取当前槽位
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
                
                # 验证槽位是否有效
                main_py = os.path.join(slot_path, "main.py")
                if os.path.exists(main_py):
                    use_slot = True
                    logk.printl("launcher", "槽位有效，将从槽位加载系统文件", boot_time)
                else:
                    logk.printl("launcher", "槽位无效，将从src目录加载系统文件", boot_time)
        except Exception as e:
            logk.printl("launcher", f"读取槽位文件失败: {e}，将从src目录加载系统文件", boot_time)
    else:
        logk.printl("launcher", "未找到槽位文件，将从src目录加载系统文件", boot_time)
    
    # 确定系统文件加载路径
    if use_slot:
        # 从槽位加载系统文件
        system_path = slot_path
        logk.printl("launcher", f"从槽位加载系统文件: {system_path}", boot_time)
    else:
        # 从src目录加载系统文件
        system_path = os.path.join(root_dir, "src")
        logk.printl("launcher", f"从src目录加载系统文件: {system_path}", boot_time)
    
    # 验证系统文件完整性
    main_py = os.path.join(system_path, "main.py")
    if not os.path.exists(main_py):
        logk.printl("launcher", f"错误: 找不到 main.py: {main_py}", boot_time)
        logk.printl("launcher", "系统文件不完整，无法启动", boot_time)
        sys.exit(1)
    
    # 将系统路径添加到Python路径
    if system_path not in sys.path:
        sys.path.insert(0, system_path)
    
    # 将apps目录添加到Python路径
    apps_path = os.path.join(system_path, "apps")
    if os.path.exists(apps_path) and apps_path not in sys.path:
        sys.path.insert(0, apps_path)
    
    # 切换到系统目录
    original_dir = os.getcwd()
    os.chdir(system_path)
    logk.printl("launcher", f"工作目录: {os.getcwd()}", boot_time)
    
    try:
        # 导入并运行main模块
        logk.printl("launcher", "加载主程序...", boot_time)
        
        # 使用importlib动态导入main模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", main_py)
        main_module = importlib.util.module_from_spec(spec)
        sys.modules['main'] = main_module
        
        # 标记已通过启动器启动
        sys._launcher_detected = True
        
        # 执行main模块
        spec.loader.exec_module(main_module)
        
        # 显式调用main()函数（因为使用importlib导入时__name__不是"__main__"）
        if hasattr(main_module, 'main'):
            main_module.main()
        
        logk.printl("launcher", "PySpOS 启动完成", boot_time)
        
    except Exception as e:
        logk.printl("launcher", f"启动失败: {e}", boot_time)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 恢复原始目录（如果需要）
        # os.chdir(original_dir)
        pass

if __name__ == "__main__":
    main()