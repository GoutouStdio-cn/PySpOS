#
#   logk.py
#   日志处理和打印
#
#   2026/1/23 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import time
from typing import Optional

# 格式化时间戳
def _format_timestamp(elapsed: float) -> str:
    return f"{elapsed:10.6f}"

# 获取启动时间
def get_boot_time() -> float:
    return time.time()

# 打印一条日志
def printl(
    module: str,
    message: str,
    boot_time: Optional[float] = None
) -> None:
    # 初始化基准时间
    if boot_time is None:
        boot_time = time.time()
    
    # 计算流逝时间并格式化时间戳
    elapsed = time.time() - boot_time
    timestamp = _format_timestamp(elapsed)
    
    # 拼接并打印最终日志行
    log_line = f"[{timestamp}] {module}: {message}"
    print(log_line)