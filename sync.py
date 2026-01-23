#
#   sync.py
#   同步文件功能
#
#   2026/1/23 by GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import os
import shutil
import printk

# 定义必须同步的文件
REQUIRED_FILES = [
    "kernel.py", "main.py", "fs.py", "printk.py", "sync.py", "btcfg.py"
]
# 定义必须同步的目录
REQUIRED_DIRS = ["apps", "etc"]

# 获取文件大小
def get_file_size(path: str) -> int:
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except Exception as e:
            printk.warn(f"获取文件大小失败 {path}: {str(e)}")
            return -1
    return 0

# 从fix文件夹同步文件
def sync_file_from_fix(src_path: str, dest_path: str) -> bool:
    if not os.path.exists(src_path):
        printk.warn(f"源文件不存在，跳过同步: {src_path}")
        return False
    
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    
    src_size = get_file_size(src_path)
    dest_size = get_file_size(dest_path)
    
    # 检查文件大小
    if src_size == dest_size and src_size != -1:
        printk.info(f"文件大小一致，无需同步: {os.path.basename(dest_path)}")
        return True
    
    try:
        shutil.copy2(src_path, dest_path)
        printk.ok(f"同步文件成功: {os.path.basename(src_path)} -> {dest_path}")
        return True
    except Exception as e:
        printk.error(f"同步文件失败 {src_path} -> {dest_path}: {str(e)}")
        return False

# 递归同步目录
def sync_dir_from_fix(src_dir: str, dest_dir: str) -> bool:
    if not os.path.isdir(src_dir):
        printk.warn(f"源目录不存在，跳过同步: {src_dir}")
        return False
    
    os.makedirs(dest_dir, exist_ok=True)
    sync_success = True
    
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        if os.path.isfile(src_item):
            if not sync_file_from_fix(src_item, dest_item):
                sync_success = False
        elif os.path.isdir(src_item):
            if not sync_dir_from_fix(src_item, dest_item):
                sync_success = False
    
    return sync_success

# 将fix目录文件同步到根目录
def sync_fix_to_root() -> bool:
    root_dir = os.path.abspath(os.path.dirname(__file__))
    fix_dir = os.path.join(root_dir, "fix")
    
    if not os.path.isdir(fix_dir):
        printk.error(f"fix目录不存在！路径: {fix_dir}")
        return False
    
    printk.info(f"开始同步fix目录到根目录")
    printk.info(f"项目根目录: {root_dir}")
    printk.info(f"源文件目录(fix): {fix_dir}")
    print()
    
    total_success = True
    
    # 同步必须文件到根目录
    for file_name in REQUIRED_FILES:
        src_file = os.path.join(fix_dir, file_name)
        dest_file = os.path.join(root_dir, file_name)
        if not sync_file_from_fix(src_file, dest_file):
            total_success = False
    
    # 同步目录到根目录
    for dir_name in REQUIRED_DIRS:
        src_dir = os.path.join(fix_dir, dir_name)
        dest_dir = os.path.join(root_dir, dir_name)
        if not sync_dir_from_fix(src_dir, dest_dir):
            total_success = False
    
    if total_success:
        printk.ok("根目录同步完成")
    else:
        printk.warn("部分文件同步失败，请检查日志")
    
    return total_success

if __name__ == "__main__":
    sync_fix_to_root()