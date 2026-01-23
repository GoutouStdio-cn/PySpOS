# main.py - PySpOS 主程序入口

import os
import printk
import platform
import kernel
import fs
import sys
import btcfg
import uuid
import re

# 设置 apps 目录为模块搜索路径
current_dir = os.getcwd()
apps_dir = os.path.join(current_dir, 'apps')
sys.path.append(apps_dir)

# 全局变量定义处
bootcfg = btcfg.load_bootcfg()
rootstate = bool(btcfg.get_bootcfg('rootstate'))

# 主函数
def main():
    printk.info("加载 PySpKernel...")
    if not btcfg.get_bootcfg('locked'):
        print("")
    printk.info(f"Bootloader：{"已上锁" if bootcfg['locked'] else "已解锁"}，ROOT 权限：{"未启用" if not bootcfg['rootstate'] else "已启用"}")
    printk.ok(f"加载完成，您使用的操作系统为：{sys.platform}, 你的设备id为：{uuid.getnode()}")
    
    printk.ok("ROOT 状态：" + "已启用" if rootstate else "未启用")
    kernel.loop()

def print_sunhb():
    cores = kernel.cores
    print(f"‘shb’程序将打印孙浩博是小可爱！{cores}次。\n")
    print("孙浩博是 " * cores)
    print("小可爱！ " * cores)
    print()

# 处理命令
def handle_command(prompt):
    if prompt == "help":
        print("clear      清屏")
        print("echo       打印指定的字符串")
        print("osver      查看系统和Python版本")
        print("shutdown   关闭PySpOS")
        print("python     启动Python")
        print("shb        打印孙浩博是小可爱 n 次（n 指你的CPU逻辑核心数）")
        print("ls/dir     列出当前目录下的文件和文件夹")
        print("finfo      查看指定文件的信息")
        print("testroot   测试ROOT权限")
        print("open       运行 apps 目录下的指定应用程序\n")
    elif prompt.startswith("echo "):
        text = prompt[5:].strip()
        print(f"{text}\n")
    elif prompt.startswith("open "):
        text = prompt[5:].strip()
        # 自动添加 .py 后缀
        if not text.endswith(".py"):
            text += ".py"
        
        # 路径安全检查
        if re.search(r'\.\./', text) or os.path.isabs(text):
            printk.error("错误：文件名不允许包含 ../ 或绝对路径\n")
            return
        try:
            # 获取 main.py 所在目录
            root_dir = os.path.dirname(os.path.abspath(__file__))
            app_path = os.path.join(root_dir, "apps", text)
            
            # 检查文件是否存在且为文件
            if not os.path.exists(app_path) or not os.path.isfile(app_path):
                printk.error(f"未找到可执行文件: {text}\n")
                return
            
            # 读取文件内容
            with open(app_path, 'r', encoding='utf-8') as f:
                code = f.read()

            exec_namespace = globals().copy()
            exec_namespace["__name__"] = "__exec__"  # 自定义的 __name__
            
            # 执行代码并传入全局上下文
            exec(code, exec_namespace)
            printk.ok(f"应用 {text} 已退出\n")
        
        except Exception as e:
            printk.error(f"执行 {text} 失败: {str(e)}\n")
    elif prompt == "echo":
        print("Usage: echo 指定的字符串\n")
    elif prompt == "osver":
        print(f"OS Version: 3.14.15-PySpOS\n")
        print(f"Kernel(Python) Version:{platform.python_version()}\n")
    elif prompt == "shutdown":
        kernel.exit()
    elif prompt == "clear":
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
    elif prompt == "python":
        os.system("python")
        print()
    elif prompt == "shb":
        print_sunhb()
    elif prompt in ("ls", "dir"):
        items = fs.list_dir()
        for item in items:
            print(item)
        print()
    elif prompt.startswith("finfo "):
        text = prompt[6:].strip()
        info = fs.get_file_info(text)
        if info:    
            print(f"{text} 的文件信息\n大小: {info['size']} 字节, 修改时间: {info['modified']}, 是否为目录: {info['is_dir']}\n")
        else:
            print(f"未找到文件或目录: {text}\n")    
    elif prompt == "testroot":
        if rootstate:
            print("当前处于 ROOT 权限状态。")
            print(f"rootstate 变量值为: {rootstate}\n")
        else:
            print("当前未处于 ROOT 权限状态。")
            print(f"rootstate 变量值为: {rootstate}\n")
    else:
        print(f"'{prompt}' 不是内部或外部命令，也不是可运行的程序或批处理文件。\n")

if __name__ == "__main__":
    main()