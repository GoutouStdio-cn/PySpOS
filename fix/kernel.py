# kernel.py - PySpOS 内核处理

import printk
import os
import sys
import subprocess
import main
import time
import api
import shutil
import ota
import sync

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
    raise RuntimeError(
        "(null)"
    )

def load_slot_system(slot: str) -> bool:
    """加载指定槽位的系统文件（核心生效逻辑）"""
    required_files = ["kernel.py", "main.py", "fs.py"]  # 系统核心文件
    for file in required_files:
        src = os.path.join(slot, file)
        dest = os.path.join(os.getcwd(), file)  # 覆盖根目录文件
        if not os.path.exists(src):
            printk.error(f"槽位 {slot} 缺少核心文件: {file}")
            return False
        
        # 复制文件覆盖当前系统
        try:
            shutil.copy2(src, dest)
            printk.info(f"已加载 {slot} 中的 {file}")
        except Exception as e:
            printk.error(f"加载文件失败: {str(e)}")
            return False
    return True


def loop():
    current_slot = ota.get_current_slot()
    printk.info(f"正在加载槽位 {current_slot} 的PySpOS...")
    if not os.path.exists(current_slot):
        printk.warn(f"槽位 {current_slot} 不存在，正在创建默认槽位 A...")
        sync.sync_fix_to_slots()
    if not load_slot_system(current_slot):
        printk.error("系统加载失败，尝试回退到默认槽位")
        fallback_slot = ota.SLOT_A if current_slot == ota.SLOT_B else ota.SLOT_B
        if load_slot_system(fallback_slot):
            ota.set_current_slot(fallback_slot)
            current_slot = fallback_slot
        else:
            printk.error("All slots failed to load. The system has been destroyed.")
            while 1:
                pass

    username = get_system_username()
    cores = os.cpu_count()  # CPU 逻辑核心数量
    printk.ok(f"kernel.py: 已加载 {current_slot} 的 PySpOS！")
    print()
    print("孙浩博 "* cores)
    print("小可爱 "* cores)
    print()
    print("欢迎使用 PySpOS 操作系统！")
    print() # 打印一个空行
    while 1:
        try:
            current_dir = os.getcwd()
            current_dir_name = os.path.basename(current_dir)

            if (main.rootstate):
                prompt = input(f"\033[91m{username}@PySPOS (ROOT)\033[0m:\033[94m/%s$ \033[0m" % current_dir_name)
            else:
                prompt = input(f"\033[92m{username}@PySPOS\033[0m:\033[94m/%s$ \033[0m" % current_dir_name)
            
            main.handle_command(prompt)

        except Exception as e:
            printk.error(f"{e}")

# 安全退出
def exit():
    if os.path.isdir("__pycache__"):
        try:
            import shutil
            shutil.rmtree("__pycache__")
            shutil.rmtree("apps/__pycache__")
            printk.ok("已删除缓存目录 __pycache__")
        except Exception as e:
            printk.error(f"无法删除缓存目录: {e}")
    else:
        printk.warn("未找到缓存目录 __pycache__，无需删除")
    
    if os.path.isdir("apps/__pycache__"):
        try:
            import shutil
            shutil.rmtree("apps/__pycache__")
            printk.ok("已删除软件缓存目录 apps/__pycache__")
        except Exception as e:
            printk.error(f"无法删除缓存目录: {e}")
    else:
        printk.warn("未找到软件缓存目录 apps/__pycache__，无需删除")
    printk.info("正在关闭 PySpOS 操作系统...")
    time.sleep(1)
    sys.exit(0)