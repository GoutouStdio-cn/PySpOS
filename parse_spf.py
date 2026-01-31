#
#   parse_spf.py
#   spf解析功能（移植的SpaceOS的spf解析器，跟那个不大一样）
#
#   2026/1/31 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import gc
import logk
import main
import pyspos

# 全局变量，控制运行日志是否开启（如果系统开发阶段为alpha或开发者模式则开启，那时候很需要）
if pyspos.OS_DEVELOP_STAGE == "alpha" or pyspos.DEVELOPER_MODE:
    run_log_enabled = 1
else:
    run_log_enabled = 0

# 运行指定路径的spf文件
def run_spf(spf_path):
    if not spf_path : raise SyntaxError("path is null") # C语言写习惯了，在哪都加个空判断

    try:
        code = ''
        # 打开spf文件
        with open(spf_path, 'r', encoding='utf-8') as f:
            code = f.read()

        code = "\n".join([line.strip().replace("\t", "") for line in code.splitlines() if line.strip()])
        if run_log_enabled:
            print(f"File contant:\n{code}")
        if not code: raise SyntaxError("An error occurred while reading the spf file, the file may be empty or corrupted")

        # 代码内容
        commands = [cmd.strip() for cmd in code.split(";") if cmd.strip()]

        # 遍历执行代码
        for cmd in commands:
            if cmd.startswith("putchar(") and cmd.endswith(")"):
                param = cmd[8: -1].strip() # 中间的那个字符串
                # 检查字符串是否被""包裹
                if not (param.startswith('"') and param.endswith('"')):
                    raise SyntaxError(f"putchar parameter must be string, got {param}")
                output_str = param[1:-1]
                print(output_str)
            elif cmd.startswith("exit(") and cmd.endswith(")"):
                param = cmd[5: -1].strip()
                if not param:
                    raise SyntaxError("You must provide an exit code")
                if run_log_enabled:
                    logk.printl("parser_spf", f"SPF file path: {spf_path} is exited, exitcode is {int(param)}", main.boot_time)
                print()
                return # 退出spf程序
            else:
                raise SyntaxError(f"Unknown code {cmd}")
        # 执行gc垃圾回收
        gc.collect()
    except Exception as i:
        logk.printl("parser_spf", f"spf run has fatal error: {i}", main.boot_time)