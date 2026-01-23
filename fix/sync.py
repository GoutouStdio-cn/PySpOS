# sync.py - 从fix目录同步核心文件到根目录的A/B槽位（仅文件大小不同时同步）
import os
import shutil
import printk
from ota import SLOT_A, SLOT_B

# 定义必须同步的核心文件（fix目录下的关键文件）
REQUIRED_FILES = [
    "kernel.py", "main.py", "fs.py", "printk.py", "ota.py", "sync.py"
]
# 定义必须同步的目录（递归同步）
REQUIRED_DIRS = ["apps"]

def get_file_size(path: str) -> int:
    """
    获取文件大小（字节），目录返回0
    :param path: 文件/目录路径
    :return: 字节数（目录返回0）
    """
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except Exception as e:
            printk.warn(f"获取文件大小失败 {path}: {str(e)}")
            return -1
    return 0

def sync_file_from_fix(src_path: str, dest_path: str) -> bool:
    """
    从fix目录复制单个文件到目标路径（仅大小不同时执行）
    :param src_path: fix目录下源文件的绝对路径
    :param dest_path: 目标槽位中文件的绝对路径
    :return: 同步是否成功
    """
    # 检查源文件是否存在
    if not os.path.exists(src_path):
        printk.warn(f"源文件不存在，跳过同步: {src_path}")
        return False
    
    # 确保目标目录存在（比如slot_a/）
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    
    # 对比文件大小：仅大小不同时复制
    src_size = get_file_size(src_path)
    dest_size = get_file_size(dest_path)
    
    if src_size == dest_size and src_size != -1:
        printk.info(f"文件大小一致，无需同步: {os.path.basename(dest_path)}")
        return True
    
    # 执行文件复制（保留元数据：修改时间、权限等）
    try:
        shutil.copy2(src_path, dest_path)
        printk.ok(f"同步文件成功: {os.path.basename(src_path)} -> {dest_path}")
        return True
    except Exception as e:
        printk.error(f"同步文件失败 {src_path} -> {dest_path}: {str(e)}")
        return False

def sync_dir_from_fix(src_dir: str, dest_dir: str) -> bool:
    """
    递归同步目录（仅文件大小不同时复制文件）
    :param src_dir: fix目录下源目录的绝对路径
    :param dest_dir: 目标槽位中目录的绝对路径
    :return: 同步是否成功
    """
    # 检查源目录是否存在
    if not os.path.isdir(src_dir):
        printk.warn(f"源目录不存在，跳过同步: {src_dir}")
        return False
    
    # 确保目标目录存在
    os.makedirs(dest_dir, exist_ok=True)
    sync_success = True
    
    # 遍历目录内所有文件/子目录
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        if os.path.isfile(src_item):
            # 同步单个文件
            if not sync_file_from_fix(src_item, dest_item):
                sync_success = False
        elif os.path.isdir(src_item):
            # 递归同步子目录
            if not sync_dir_from_fix(src_item, dest_item):
                sync_success = False
    
    return sync_success

def sync_fix_to_slots() -> bool:
    """
    核心同步函数：将fix目录的文件同步到根目录的slot_a/slot_b（仅大小不同时）
    :return: 整体同步是否成功
    """
    # 关键修复：获取项目根目录（当前sync.py所在目录的父目录）
    # 例如：slot_a/sync.py -> 父目录为项目根目录
    current_sync_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.dirname(current_sync_dir)  # 从槽位目录上移到项目根目录
    
    # 检查根目录是否存在
    if not os.path.isdir(root_dir):
        printk.error(f"项目根目录不存在！路径: {root_dir}")
        return False
    
    printk.info(f"=== 开始同步到根目录槽位 ===")
    printk.info(f"项目根目录路径: {root_dir}")
    print()
    
    # 同步到A/B两个槽位
    total_success = True
    for slot in [SLOT_A, SLOT_B]:
        printk.info(f"--- 处理槽位: {slot} ---")
        # 槽位的绝对路径（项目根目录/slot_a 或 项目根目录/slot_b）
        slot_dir = os.path.join(root_dir, slot)
        
        # 同步核心文件（从项目根目录读取源文件）
        for file_name in REQUIRED_FILES:
            src_file = os.path.join(root_dir, file_name)
            dest_file = os.path.join(slot_dir, file_name)
            if not sync_file_from_fix(src_file, dest_file):
                total_success = False
        
        # 同步目录（从项目根目录读取源目录）
        for dir_name in REQUIRED_DIRS:
            src_dir = os.path.join(root_dir, dir_name)
            dest_dir = os.path.join(slot_dir, dir_name)
            if not sync_dir_from_fix(src_dir, dest_dir):
                total_success = False
        
        print()
    
    if total_success:
        printk.ok("=== 所有槽位同步完成 ===")
    else:
        printk.error("=== 部分文件同步失败，请检查日志 ===")
    
    return total_success

# 测试入口（当极端情况时，比如main.py炸了） 
if __name__ == "__main__":
    sync_fix_to_slots()