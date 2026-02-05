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

def confirm(prompt: str) -> bool:
    while True:
        # 拼接提示信息，末尾添加 [y/n]
        user_input = input(f"{prompt}(y/n): ").strip().lower()
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            # 无效输入时提示重新输入
            print(f"\033[33m无效输入：{user_input}，请输入 y 或 n\033[0m")