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

        # 稍微改了一下处理方式，去掉注释和多余空白
        code = "".join([
            line.strip().replace("\t", "") 
            for line in code.splitlines() 
            if line.strip() and not (line.strip().startswith("#") or line.strip().startswith("//"))
        ])
        if run_log_enabled:
            print(f"File content:\n{code}")
        if not code: raise SyntaxError("An error occurred while reading the spf file, the file may be empty or corrupted")

        # 确保代码末尾有分号
        code = code.rstrip() + ";"
        # 代码内容
        commands = [cmd.strip() for cmd in code.split(";") if cmd.strip()]

        # 遍历执行代码
        for cmd in commands:
            try:
                # 我们先清除cmd前后的空白字符
                cmd_stripped = cmd.strip()
                
                # 注释处理
                if cmd_stripped.startswith("#") or cmd_stripped.startswith("//"):
                    continue
                # 空命令跳过
                if not cmd_stripped:
                    continue
                
                # 处理putchar命令
                if cmd_stripped.startswith("putchar(") and cmd_stripped.endswith(")"):
                    param = cmd_stripped[8: -1]
                    param_stripped = param.strip()
                    
                    # 检查参数是否被""包裹
                    if not (param_stripped.startswith('"') and param_stripped.endswith('"')):
                        raise SyntaxError(f"putchar parameter must be string, got {param_stripped}")
                    
                    output_str = param_stripped[1:-1]
                    print(output_str)
                
                # 处理exit命令
                elif cmd_stripped.startswith("exit(") and cmd_stripped.endswith(")"):
                    param = cmd_stripped[5: -1].strip()
                    if not param:
                        raise SyntaxError("You must provide an exit code")
                    if run_log_enabled:
                        logk.printl("parser_spf", f"SPF file path: {spf_path} is exited, exitcode is {int(param)}", main.boot_time)
                    print()
                    return  # 退出spf程序
                
                # 未知命令
                else:
                    raise SyntaxError(f"Unknown code {cmd_stripped}")
            except Exception as cmd_err:
                logk.printl("parser_spf", f"cmd '{cmd}' execute failed: {cmd_err}", main.boot_time)
                continue
        
        # 执行gc垃圾回收
        gc.collect()
    
    # 捕获异常
    except Exception as i:
        logk.printl("parser_spf", f"spf run has fatal error: {i}", main.boot_time)
pass # RUN_SPF