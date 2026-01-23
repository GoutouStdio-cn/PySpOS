# printk.py - 打印信息模块

# 颜色定义
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
RESET_COLOR = "\033[0m"
YELLOW_COLOR = "\033[93m"

# 打印带有 [ OK ] 前缀的字符串
def ok(message: str) -> None:
    print(f"[{GREEN_COLOR} OK {RESET_COLOR}] {message}")

# 打印带有 [ ERROR ] 前缀的字符串
def error(message: str) -> None:
    print(f"[{RED_COLOR} ERROR {RESET_COLOR}] {message}")

# 打印带有 [ WARN ] 前缀的字符串
def warn(message: str) -> None:
    print(f"[{YELLOW_COLOR} WARN {RESET_COLOR}] {message}")

# 打印带有 [ INFO ] 前缀的字符串
def info(message: str) -> None:
    print(f"[ INFO ] {message}")