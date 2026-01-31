#
#   parse_spf.py
#   spf解析功能
#
#   2026/1/31 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import gc
import logk
import main

# 全局变量，控制运行日志是否开启
run_log_enabled = 1

# 运行指定路径的spf文件
def run_spf(spf_path):
    if not spf_path : raise SystemError("path为空") # c写习惯了在哪都加个空判断

    try:
        code = ''
        # 打开spf文件
        with open(spf_path, 'r', encoding='utf-8') as f:
            code = f.read()
        if run_log_enabled:
            logk.printl("parser_spf", f"spf 文件内容：{code}", main.boot_time)

        code = "\n".join([line.strip().replace("\t", "") for line in code.splitlines() if line.strip()])
        if run_log_enabled:
            print(f"File contant: {code}")
        if not code: raise SystemError("读取spf文件时出现错误")

        # 命令
        commands = [cmd.strip() for cmd in code.split(";") if cmd.strip()]

        for cmd in commands:
            if cmd.startswith("putchar(") and cmd.endswith(")"):
                param = cmd[8: -1].strip() # 中间的那个字符串
                # 检查字符串是否被""包裹
                if not (param.startswith('"') and param.endswith('"')):
                    raise SyntaxError(f"putchar参数需双引号包裹，执行失败")
                output_str = param[1:-1]
                print(output_str)
            elif cmd.startswith("exit(") and cmd.endswith(")"):
                param = cmd[5: -1].strip()
                if not param:
                    raise SyntaxError("未指定退出号")
                if run_log_enabled:
                    logk.printl("parser_spf", f"SPF 文件地址：{spf_path}已退出，退出号为{int(param)}", main.boot_time)
                print()
                return
            else:
                raise SyntaxError(f"未知命令：{cmd}，执行失败")
        # gc垃圾回收
        gc.collect()
    except Exception as i:
        logk.printl("parser_spf", f"spf运行出现未知错误：{i}", main.boot_time)