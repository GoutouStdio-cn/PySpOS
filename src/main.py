#  
#   main.py
#   PySpOS 入口
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import os
import printk
import platform
import kernel
import fs
import sys
import btcfg
import re
import logk
import recovery
import pyspos
import ota

# 检查是否通过启动器启动
if not hasattr(sys, '_launcher_detected'):
    raise RuntimeError("请使用启动器（launcher）启动PySpOS！")
    sys.exit(1)

# 标记已通过启动器启动
sys._launcher_detected = True

if pyspos.SPF_ENABLED:
    import parse_spf
else:
    class parse_spf:
        @staticmethod
        # 占位符，因为此时 SPF_ENABLED 为假
        def run_spf(spf_path):
            raise NotImplementedError("SPF support is disabled in this build. spf path: " + spf_path)

# 设置 apps 目录为模块搜索路径
current_dir = os.getcwd()
apps_dir = os.path.join(current_dir, 'apps')
sys.path.append(apps_dir)

# 全局变量定义处
bootcfg = btcfg.load_bootcfg()
rootstate = bool(btcfg.get_bootcfg('rootstate'))
boot_time = logk.get_boot_time()

# 获取根目录（main.py所在目录的父目录）
script_dir = os.path.dirname(os.path.abspath(__file__))

# 检查是否在src目录或槽位目录中
if os.path.basename(script_dir) == 'src':
    # 在src目录中，根目录是src的父目录
    root_dir = os.path.dirname(script_dir)
    in_slot = False
elif os.path.basename(script_dir) in ['slot_a', 'slot_b']:
    # 在槽位目录中，根目录是槽位的父目录
    root_dir = os.path.dirname(script_dir)
    in_slot = True
else:
    # 其他情况，使用当前目录作为根目录
    root_dir = script_dir
    in_slot = False

# 切换到当前槽位目录
current_slot_file = os.path.join(root_dir, "current_slot")
if os.path.exists(current_slot_file):
    try:
        with open(current_slot_file, 'r') as f:
            current_slot = f.read().strip()
            slot_path = os.path.join(root_dir, current_slot)
            if os.path.exists(slot_path):
                # 如果当前不在槽位目录中，切换到槽位目录
                if not in_slot:
                    os.chdir(slot_path)
                    current_dir = os.getcwd()
                    apps_dir = os.path.join(current_dir, 'apps')
                    sys.path.append(apps_dir)
                    logk.printl("main", f"已切换到槽位: {current_slot}", boot_time)
                else:
                    # 已经在槽位目录中，保持当前目录
                    logk.printl("main", f"当前已在槽位: {current_slot}", boot_time)
            else:
                logk.printl("main", f"槽位 {current_slot} 不存在，使用src目录", boot_time)
    except Exception as e:
        logk.printl("main", f"读取槽位文件失败: {e}，使用src目录", boot_time)
else:
    logk.printl("main", "未找到槽位文件，使用src目录", boot_time)

# 获取应用路径
def get_app_path(app_name: str) -> str:
    # 使用当前工作目录的apps目录
    return os.path.join(os.getcwd(), "apps", app_name)

# 获取spf应用路径
def get_spf_path(app_name: str) -> str:
    # 使用当前工作目录的spfapps目录
    return os.path.join(os.getcwd(), "spfapps", app_name)

# 验证文件名安全性
def is_safe_filename(filename: str) -> bool:
    return not (re.search(r'\.\./', filename) or os.path.isabs(filename))

# 主函数
def main():
    logk.printl("main", "加载 PySpKernel...", boot_time)
    logk.printl("main", f"Bootloader：{"已上锁" if bootcfg['locked'] else "已解锁"}，ROOT 权限：{"未启用" if not bootcfg['rootstate'] else "已启用"}", boot_time)
    logk.printl("main", f"加载完成，您使用的操作系统为：{sys.platform}", boot_time)
    logk.printl("main",  "ROOT已启用" if rootstate else "ROOT未启用", boot_time)

    kernel.loop()

# 打印孙浩博是小可爱
def print_sunhb():
    cores = kernel.cores
    print(f"'shb'程序将打印孙浩博是小可爱！{cores}次。\n")
    print("孙浩博是 " * cores)
    print("小可爱！ " * cores)
    print()

# 命令处理函数
def cmd_help():
    print("clear      清屏")
    print("echo       打印指定的字符串")
    print("osver      查看系统和Python版本")
    print("shutdown   关闭PySpOS")
    print("python     启动Python")
    print("shb        打印孙浩博是小可爱 n 次（n 指你的CPU逻辑核心数）")
    print("ls/dir     列出当前目录下的文件和文件夹")
    print("finfo      查看指定文件的信息")
    print("testroot   测试ROOT权限")
    print("open       运行 apps 目录下的指定应用程序")
    print("ota_check  检查是否有可用的更新")
    print("ota_update 下载并安装更新")
    print("ota_status 查看OTA更新状态")
    print("ota_rollback 回滚到上一个版本")
    print("ota_clean  清理更新包文件\n")

def cmd_echo(text: str):
    print(f"{text}\n")

def cmd_osver():
    print(f"PySpOS 版本: {pyspos.OS_VERSION}, 开发阶段: {pyspos.OS_DEVELOP_STAGE}")
    print(f"Python 版本: {platform.python_version()}\n")

def cmd_shutdown():
    kernel.exit()

def cmd_clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def cmd_python():
    os.system("python")
    print()

def cmd_recovery():
    recovery.recovery_main("kernel_jump")

def cmd_shb():
    print_sunhb()

def cmd_ls():
    items = fs.list_dir()
    for item in items:
        print(item)
    print()

def cmd_finfo(filename: str):
    info = fs.get_file_info(filename)
    if info:    
        print(f"{filename} 的文件信息\n大小: {info['size']} 字节, 修改时间: {info['modified']}, 是否为目录: {info['is_dir']}\n")
    else:
        print(f"未找到文件或目录: {filename}\n")

def cmd_testroot():
    if rootstate:
        print("当前处于 ROOT 权限状态。")
        print(f"rootstate 变量值为: {rootstate}\n")
    else:
        print("当前未处于 ROOT 权限状态。")
        print(f"rootstate 变量值为: {rootstate}\n")

def cmd_open(app_name: str):
    if not app_name.endswith(".py"):
        app_name += ".py"
    
    if not is_safe_filename(app_name):
        printk.error("错误：文件名不允许包含 ../ 或绝对路径\n")
        return
    
    app_path = get_app_path(app_name)
    
    if not os.path.exists(app_path) or not os.path.isfile(app_path):
        printk.error(f"未找到可执行文件: {app_name}\n")
        return
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            code = f.read()

        exec_namespace = {
            '__name__': '__exec__',
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'range': range,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'bool': bool,
                'type': type,
                'isinstance': isinstance,
                'Exception': Exception,
                'ValueError': ValueError,
                'RuntimeError': RuntimeError,
                'SystemError': SystemError,
                '__import__': __import__,
            }
        }
        
        exec(code, exec_namespace)
    
    except Exception as e:
        printk.error(f"执行 {app_name} 失败: {str(e)}\n")

def cmd_openspf(app_name: str):
    if not app_name.endswith(".spf"):
        app_name += ".spf"
    
    if not is_safe_filename(app_name):
        printk.error("错误：文件名不允许包含 ../ 或绝对路径\n")
        return
    
    app_path = get_spf_path(app_name)
    
    if not os.path.exists(app_path) or not os.path.isfile(app_path):
        printk.error(f"未找到可执行文件: {app_name}\n")
        return
    
    try:
        parse_spf.run_spf(app_path)
    except Exception as e:
        printk.error(f"执行 {app_name} 失败: {str(e)}\n")

# 检查是否有可用的更新命令
def cmd_ota_check():
    update_info = ota.check_cloud_update()
    if update_info:
        if update_info['has_update']:
            print(f"发现新版本: {update_info['remote_version']}")
            print(f"当前版本: {update_info['current_version']}")
            print(f"更新内容: {update_info['release_notes']}")
        else:
            print(f"当前已是最新版本: {update_info['current_version']}")
    print()

# 下载并安装更新命令
def cmd_ota_update():
    result = ota.download_and_install_update()
    if result:
        print("更新已成功安装，系统将自动重启\n")
    else:
        print("更新失败\n")

# 查看OTA更新状态命令
def cmd_ota_status():
    status = ota.get_ota_status()
    print(f"当前槽位: {status['current_slot']}")
    print(f"当前版本: {status['current_version']}")
    print(f"其他槽位: {status['other_slot']}")
    print(f"其他版本: {status['other_version']}")
    print(f"是否有更新: {'是' if status['has_update'] else '否'}")
    if status['update_version']:
        print(f"更新版本: {status['update_version']}")
    print()

# 回滚到上一个版本命令
def cmd_ota_rollback():
    result = ota.rollback_update()
    if result:
        print("回滚成功，重启后生效\n")
    else:
        print("回滚失败\n")

# 清理更新包
def cmd_ota_clean():
    ota.clean_update_package()
    print()

# 命令映射表
COMMANDS = {
    'help': cmd_help,
    'osver': cmd_osver,
    'shutdown': cmd_shutdown,
    'clear': cmd_clear,
    'python': cmd_python,
    'recovery': cmd_recovery,
    'shb': cmd_shb,
    'ls': cmd_ls,
    'dir': cmd_ls,
    'testroot': cmd_testroot,
    'echo': lambda: print("Usage: echo 指定的字符串\n"),
    'ota_check': cmd_ota_check,
    'ota_update': cmd_ota_update,
    'ota_status': cmd_ota_status,
    'ota_rollback': cmd_ota_rollback,
    'ota_clean': cmd_ota_clean,
}

# 处理命令
def handle_command(prompt) -> str:
    if prompt in COMMANDS:
        COMMANDS[prompt]()
    elif prompt.startswith("echo "):
        cmd_echo(prompt[5:].strip())
    elif prompt.startswith("open "):
        cmd_open(prompt[5:].strip())
    elif prompt.startswith("openspf "):
        cmd_openspf(prompt[8:].strip())
    elif prompt.startswith("finfo "):
        cmd_finfo(prompt[6:].strip())
    else:
        print(f"'{prompt}' 不是内部或外部命令，也不是可运行的程序或批处理文件。\n")

if __name__ == "__main__":
    main()