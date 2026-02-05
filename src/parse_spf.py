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
    if not spf_path:
        raise SyntaxError("path is null")

    try:
        with open(spf_path, 'r', encoding='utf-8') as f:
            code = f.read()

        lines = code.splitlines()
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not (stripped.startswith("#") or stripped.startswith("//")):
                cleaned_lines.append(stripped)
        
        code = "".join(cleaned_lines)
        if run_log_enabled:
            print(f"File content:\n{code}")
        if not code:
            raise SyntaxError("An error occurred while reading the spf file, the file may be empty or corrupted")

        code = code.rstrip() + ";"
        commands = [cmd.strip() for cmd in code.split(";") if cmd.strip()]

        for cmd in commands:
            try:
                cmd_stripped = cmd.strip()
                
                if cmd_stripped.startswith("#") or cmd_stripped.startswith("//"):
                    continue
                if not cmd_stripped:
                    continue
                
                if cmd_stripped.startswith("putchar(") and cmd_stripped.endswith(")"):
                    param = cmd_stripped[8:-1].strip()
                    
                    if not (param.startswith('"') and param.endswith('"')):
                        raise SyntaxError(f"putchar parameter must be string, got {param}")
                    
                    output_str = param[1:-1]
                    print(output_str)
                
                elif cmd_stripped.startswith("exit(") and cmd_stripped.endswith(")"):
                    param = cmd_stripped[5:-1].strip()
                    if not param:
                        raise SyntaxError("You must provide an exit code")
                    if run_log_enabled:
                        logk.printl("parser_spf", f"SPF file path: {spf_path} is exited, exitcode is {int(param)}", main.boot_time)
                    print()
                    return
                
                else:
                    raise SyntaxError(f"Unknown code {cmd_stripped}")
            except Exception as cmd_err:
                logk.printl("parser_spf", f"cmd '{cmd}' execute failed: {cmd_err}", main.boot_time)
                continue
        
        gc.collect()
    
    except Exception as i:
        logk.printl("parser_spf", f"spf run has fatal error: {i}", main.boot_time)