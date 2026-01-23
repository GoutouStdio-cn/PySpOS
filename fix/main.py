# main.py - PySpOS 主程序入口

import os
import printk
import platform
import kernel
import fs
import sys

# 设置 apps 目录为模块搜索路径
current_dir = os.getcwd()
apps_dir = os.path.join(current_dir, 'apps')
sys.path.append(apps_dir)

# 导入 api 模块
import api

# 全局变量 rootstate（此接口以后再用）
rootstate = False

# main function
def main():
    printk.info("加载 PySpKernel...")
    printk.ok(f"加载完成，您使用的操作系统为：{os.name}")

    kernel.loop()

# 处理命令
def handle_command(prompt):
    if prompt == "help":
        print("echo       打印指定的字符串")
        print("osver      查看系统和Python版本")
        print("shutdown   关闭PySpOS")
        print("python     启动Python")
        print("ls/dir     列出当前目录下的文件和文件夹")
        print("finfo      查看指定文件的信息")
        print("open       运行 apps 目录下的指定应用程序\n")
        print()
    elif prompt.startswith("echo "):
        text = prompt[5:].strip()
        print(f"{text}\n")
    elif prompt.startswith("open "):
        text = prompt[5:].strip()
        # 如果没添加后缀，自动添加 .py 后缀
        if text.endswith(".py"):
            pass
        else:
            text += ".py"
        
        # 检查文件是否存在
        if not os.path.exists(f"apps/{text}"):
            print(f"未找到可执行文件: {text}\n")
            return
        
        code = fs.read_file(f"apps/{text}")
        exec(code)
        print()            
    elif prompt == "echo":
        print("Usage: echo 指定的字符串\n")
    elif prompt == "osver":
        print(f"OS Version: 3.14.15-PySpOS\n")
        print(f"Kernel(Python) Version:{platform.python_version()}\n")
    elif prompt == "shutdown":
        kernel.exit()
    elif prompt == "python":
        os.system("python")
        print()
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
            print("当前处于 ROOT 权限状态。\n")
            print(f"rootstate 变量值为: {rootstate}\n")
        else:
            print("当前未处于 ROOT 权限状态。\n")
            print(f"rootstate 变量值为: {rootstate}\n")
    else:
        print(f"'{prompt}' 不是内部或外部命令，也不是可运行的程序或批处理文件。\n")

if __name__ == "__main__":
    main()