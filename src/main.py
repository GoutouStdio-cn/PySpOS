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

# 导入 ELF 加载器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elf_loader import ELFRunner, run_elf, __version__ as ELF_LOADER_VERSION
from elf_loader import __develop_stage__ as ELF_LOADER_STAGE
from elf_loader import __cpu_emulator_name__ as ELF_CPU_NAME
from elf_loader import __supported_archs__ as ELF_SUPPORTED_ARCHS
from elf_loader import __syscall_abi__ as ELF_SYSCALL_ABI

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
    print("cd         切换工作目录")
    print("rm         删除文件或文件夹")
    print("finfo      查看指定文件的信息")
    print("testroot   测试ROOT权限")
    print("open       运行 apps 目录下的指定应用程序")
    print("run        加载并运行 ELF 可执行文件")
    print("ota_check  检查是否有可用的更新")
    print("ota_update 下载并安装更新")
    print("ota_status 查看OTA更新状态")
    print("ota_rollback 回滚到上一个版本")
    print("ota_clean  清理更新包文件")
    print("hotreset   热重启系统（重新加载代码）\n")

# 打印指定字符串
def cmd_echo(text: str):
    print(f"{text}\n")

# 显示PySpOS版本
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
    char = '你'
    print(f"字符：{char}")
    print(f"十六进制编码：U+{ord(char):04X}")  # 输出 U+AFAF
    print(f"十进制编码：{ord(char)}")          # 输出 44975

    # 2. 反向：从编码找字符
    code = ord(char)
    print(f"编码0x{code:04X}对应的字符：{chr(code)}")  # 输出 你

def cmd_ls():
    items = fs.list_dir()
    for item in items:
        print(item)
    print()

def cmd_cd(path: str = None):
    #切换工作目录
    if path is None or path.strip() == "":
        # 如果没有参数，切换到用户主目录
        path = os.path.expanduser("~")
    
    # 处理特殊路径
    if path == "-":
        # 切换到上一个目录
        path = os.environ.get("OLDPWD", os.getcwd())
    elif path == "~":
        path = os.path.expanduser("~")
    
    # 保存当前目录
    old_cwd = os.getcwd()
    
    try:
        # 尝试切换目录
        os.chdir(path)
        # 更新 OLDPWD 环境变量
        os.environ["OLDPWD"] = old_cwd
        # 打印当前目录
        print(os.getcwd())
    except FileNotFoundError:
        printk.error(f"cd: 没有那个文件或目录: {path}\n")
    except NotADirectoryError:
        printk.error(f"cd: 不是目录: {path}\n")
    except PermissionError:
        printk.error(f"cd: 权限拒绝: {path}\n")
    except Exception as e:
        printk.error(f"cd: 错误: {e}\n")

def cmd_finfo(filename: str):
    info = fs.get_file_info(filename) # 获取文件信息
    if info:    
        print(f"{filename} 的文件信息\n大小: {info['size']} 字节, 修改时间: {info['modified']}, 是否为目录: {info['is_dir']}\n")
    else:
        print(f"未找到文件或目录: {filename}\n")

# 删除文件或文件夹
def cmd_rm(target: str, recursive: bool = False, force: bool = False):
    if not target or target.strip() == "":
        printk.error("rm: 缺少操作数\n")
        return
    
    target = target.strip()
    
    # 安全检查
    if not is_safe_filename(target):
        printk.error("错误：文件名不允许包含 ../ 或绝对路径\n")
        return
    
    # 获取完整路径
    full_path = os.path.abspath(target)
    
    # 检查文件/文件夹是否存在
    if not os.path.exists(full_path):
        printk.error(f"rm: 无法删除 '{target}': 没有那个文件或目录\n")
        return
    
    try:
        # 判断是文件还是目录
        if os.path.isfile(full_path):
            # 删除文件
            if not force:
                if not printk.confirm(f"确认删除文件 '{target}'?"):
                    print("操作已取消\n")
                    return
            os.remove(full_path)
            printk.ok(f"已删除文件: {target}\n")
            
        elif os.path.isdir(full_path):
            # 删除目录
            if not recursive:
                printk.error(f"rm: 无法删除 '{target}': 是一个目录\n")
                print("提示: 使用 'rm -r <目录>' 递归删除目录及其内容\n")
                return
            
            if not force:
                if not printk.confirm(f"确认递归删除目录 '{target}' 及其所有内容?"):
                    print("操作已取消\n")
                    return
            
            import shutil
            shutil.rmtree(full_path)
            printk.ok(f"已删除目录: {target}\n")
            
    except PermissionError:
        printk.error(f"rm: 无法删除 '{target}': 权限拒绝\n")
    except Exception as e:
        printk.error(f"rm: 无法删除 '{target}': {str(e)}\n")

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

        exec_namespace = { # 执行命名空间
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

def cmd_run(args: str):
    """加载并运行 ELF 可执行文件
    
    用法: run [-v] [-d] [-f] <elf文件路径>
    
    选项:
        -v  显示 ELF on Windows Space 兼容层版本信息
        -d  启用调试日志模式（显示更多执行信息）
        -f  强制运行（跳过某些安全检查）
    """
    import logging
    import shlex
    
    # 解析参数
    show_version = False
    debug_mode = False
    force_mode = False
    elf_path = None
    
    # 使用 shlex 分割参数，支持引号
    try:
        tokens = shlex.split(args) if args else []
    except ValueError:
        # 引号不匹配，简单分割
        tokens = args.split() if args else []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '-v':
            show_version = True
            i += 1
        elif token == '-d':
            debug_mode = True
            i += 1
        elif token == '-f':
            force_mode = True
            i += 1
        elif token.startswith('-'):
            printk.error(f"run: 未知选项: {token}\n")
            return
        else:
            # 第一个非选项参数作为 ELF 路径
            if elf_path is None:
                elf_path = token
                i += 1
            else:
                # 额外的参数，忽略或报错
                i += 1
    
    # 显示版本信息
    if show_version:
        print(f"ELF/SPE on PySpOS (in {pyspos.OS_NAME} {pyspos.OS_VERSION} {pyspos.OS_DEVELOP_STAGE}) {ELF_LOADER_VERSION}")
        print("Copyright (C) 2022-2026 GoutouStdio.")
        print("This is free software; see the source for copying conditions.  There is NO")
        print("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
        print()
        print(f"Home page: <https://pyspos.us.ci/pyspos.html>")
        print(f"Source code: <https://github.com/GoutouStdio-cn/PySpOS>")
        print(f"Bug reports: <https://github.com/GoutouStdio-cn/PySpOS/issues>")
        print(f"             or <goutoustdio@outlook.com>")
        print()
        # 如果只指定了 -v 而没有指定文件路径，直接返回
        if elf_path is None:
            return
        print("执行ELF程序...")
    
    # 检查 ELF 路径
    if elf_path is None:
        printk.error("用法: run [-v] [-d] [-f] <elf文件路径>\n")
        return
    
    # 设置日志级别
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        logk.printl("run", f"调试模式已启用", boot_time)
        logk.printl("run", f"ELF 路径: {elf_path}", boot_time)
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # 检查文件是否存在
    if not os.path.exists(elf_path):
        # 尝试在 elf_apps 目录中查找
        alt_path = os.path.join(os.getcwd(), "elf_apps", elf_path)
        if debug_mode:
            logk.printl("run", f"尝试查找: {alt_path}", boot_time)
        if not os.path.exists(alt_path):
            alt_path = os.path.join(os.getcwd(), "test_programs", elf_path)
            if debug_mode:
                logk.printl("run", f"尝试查找: {alt_path}", boot_time)
        if os.path.exists(alt_path):
            elf_path = alt_path
            if debug_mode:
                logk.printl("run", f"找到 ELF 文件: {elf_path}", boot_time)
    
    if not os.path.isfile(elf_path):
        printk.error(f"未找到 ELF 文件: {elf_path}\n")
        return
    
    if debug_mode:
        logk.printl("run", f"文件大小: {os.path.getsize(elf_path)} 字节", boot_time)
        logk.printl("run", f"开始加载 ELF 文件...", boot_time)
    
    try:
        # 根据调试模式决定是否禁用日志
        if not debug_mode:
            logging.disable(logging.CRITICAL)
        
        # 创建 ELF 运行器
        runner = ELFRunner(elf_path)
        
        # 加载 ELF 文件
        if not runner.load():
            printk.error("ELF 文件加载失败\n")
            if not debug_mode:
                logging.disable(logging.NOTSET)
            return
        
        if debug_mode:
            logk.printl("run", f"ELF 文件加载成功", boot_time)
            logk.printl("run", f"入口点: 0x{runner.parser.header.e_entry:08X}", boot_time)
            logk.printl("run", f"架构: {'x86_64' if runner.parser.header.e_machine == 62 else 'x86'}", boot_time)
            logk.printl("run", f"程序头数量: {runner.parser.header.e_phnum}", boot_time)
            logk.printl("run", f"节头数量: {runner.parser.header.e_shnum}", boot_time)
            logk.printl("run", f"开始执行程序...", boot_time)
        
        # 运行程序
        result = runner.run()
        
        if debug_mode:
            logk.printl("run", f"程序执行完成", boot_time)
            logk.printl("run", f"退出码: {result.exit_code}", boot_time)
            logk.printl("run", f"执行指令数: {result.instruction_count}", boot_time)
            logk.printl("run", f"执行时间: {result.execution_time:.3f} 秒", boot_time)
            logk.printl("run", f"内存使用: {result.memory_usage} 字节", boot_time)
        
        # 恢复日志输出
        if not debug_mode:
            logging.disable(logging.NOTSET)
        
        # 显示程序输出
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='', file=__import__('sys').stderr)
        
    except Exception as e:
        if not debug_mode:
            logging.disable(logging.NOTSET)
        printk.error(f"运行 ELF 文件失败: {str(e)}\n")
        if debug_mode:
            import traceback
            traceback.print_exc()

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

# 热重启系统
def cmd_hotreset():
    import hotreset_env
    hotreset_env.trigger()

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
    'cd': lambda: cmd_cd(),
    'rm': lambda: printk.error("用法: rm [-r] [-f] <文件或目录>\n"),
    'testroot': cmd_testroot,
    'echo': lambda: print("用法: echo 指定的字符串\n"),
    'run': lambda: print("用法: run [-v] [-d] [-f] <elf文件路径>\n"),
    'ota_check': cmd_ota_check,
    'ota_update': cmd_ota_update,
    'ota_status': cmd_ota_status,
    'ota_rollback': cmd_ota_rollback,
    'ota_clean': cmd_ota_clean,
    'hotreset': cmd_hotreset,
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
    elif prompt.startswith("run "):
        cmd_run(prompt[4:].strip())
    elif prompt.startswith("cd "):
        cmd_cd(prompt[3:].strip())
    elif prompt.startswith("rm "):
        # 解析 rm 命令参数
        args = prompt[3:].strip()
        import shlex
        try:
            tokens = shlex.split(args) if args else []
        except ValueError:
            tokens = args.split() if args else []
        
        recursive = False
        force = False
        target = None
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '-r' or token == '-R' or token == '--recursive':
                recursive = True
                i += 1
            elif token == '-f' or token == '--force':
                force = True
                i += 1
            elif token == '-rf' or token == '-fr':
                recursive = True
                force = True
                i += 1
            elif token.startswith('-'):
                printk.error(f"rm: 未知选项: {token}\n")
                return
            else:
                if target is None:
                    target = token
                    i += 1
                else:
                    # 多个目标，处理完第一个后提示
                    break
        
        if target:
            cmd_rm(target, recursive, force)
        else:
            printk.error("rm: 缺少操作数\n")
    else:
        print(f"'{prompt}' 不是内部或外部命令，也不是可运行的程序或批处理文件。\n")

if __name__ == "__main__":
    main()